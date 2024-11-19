from __future__ import annotations

import logging
from typing import Any
from typing import Iterable

import numpy as np
from psychopy.clock import Clock
from psychopy.data import TrialHandlerExt
from psychopy.event import Mouse
from psychopy.hardware.keyboard import Keyboard
from psychopy.sound import Sound
from psychopy.visual.basevisual import BaseVisualStim
from psychopy.visual.elementarray import ElementArrayStim
from psychopy.visual.shape import ShapeStim
from psychopy.visual.window import Window

import vstt.vtypes
from vstt import joystick_wrapper
from vstt import vis
from vstt.experiment import Experiment
from vstt.geom import JoystickPointUpdater
from vstt.geom import PointRotator
from vstt.geom import to_target_dists
from vstt.stats import stats_dataframe


def _get_target_indices(outer_target_index: int, trial: dict[str, Any]) -> list[int]:
    # always include outer target index
    indices = [outer_target_index]
    if trial["add_central_target"] and not trial["automove_cursor_to_center"]:
        # add central target index
        indices.append(trial["num_targets"])
    return indices


class TrialData:
    """Stores the data from the trial that will be stored in the psychopy trial_handler"""

    def __init__(self, trial: dict[str, Any], rng: np.random.Generator):
        self.target_indices = np.fromstring(
            trial["target_indices"], dtype="int", sep=" "
        )
        if trial["target_order"] == "random":
            rng.shuffle(self.target_indices)
        self.target_pos: list[np.ndarray] = []
        self.to_target_timestamps: list[np.ndarray] = []
        self.to_target_num_timestamps_before_visible: list[int] = []
        self.to_center_timestamps: list[np.ndarray] = []
        self.to_center_num_timestamps_before_visible: list[int] = []
        self.to_target_mouse_positions: list[np.ndarray] = []
        self.to_center_mouse_positions: list[np.ndarray] = []
        self.to_target_success: list[bool] = []
        self.to_center_success: list[bool] = []


class TrialManager:
    """Stores the drawable elements and other objects needed during a trial"""

    def __init__(self, win: Window, trial: vstt.vtypes.Trial):
        self.targets = vis.make_targets(
            win,
            trial["num_targets"],
            trial["target_distance"],
            trial["target_size"],
            trial["add_central_target"],
            trial["central_target_size"],
        )
        self.drawables: list[BaseVisualStim | ElementArrayStim] = [self.targets]
        self.target_labels = None
        if trial["show_target_labels"]:
            self.target_labels = vis.make_target_labels(
                win,
                trial["num_targets"],
                trial["target_distance"],
                trial["target_size"],
                trial["target_labels"],
            )
            self.drawables.extend(self.target_labels)
        self.cursor = vis.make_cursor(win, trial["cursor_size"])
        self.cursor.setPos(np.array([0.0, 0.0]))
        if trial["show_cursor"]:
            self.drawables.append(self.cursor)
        self.point_rotator = PointRotator(trial["cursor_rotation_degrees"])
        self.joystick_point_updater = JoystickPointUpdater(
            trial["cursor_rotation_degrees"], trial["joystick_max_speed"], win.size
        )
        self._cursor_path = ShapeStim(
            win, vertices=[(0.0, 0.0)], lineColor="white", closeShape=False
        )
        self._cursor_path_vertices: list[tuple[float, float]] = []
        self.clock = Clock()
        if trial["show_cursor_path"]:
            self.drawables.append(self._cursor_path)
        self.first_target_of_condition_shown = False
        self.most_recent_target_display_time = 0.0
        self.final_target_display_time_previous_trial = 0.0
        self.green_target_index: int | None = None

    def cursor_path_add_vertex(
        self, vertex: tuple[float, float], clear_existing: bool = False
    ) -> None:
        if clear_existing:
            self._cursor_path_vertices = []
        self._cursor_path_vertices.append(vertex)
        self._cursor_path.vertices = self._cursor_path_vertices


def _contains_mixed_length_numpy_arrays(items: Iterable) -> bool:
    return (
        len(set([item.shape if isinstance(item, np.ndarray) else 1 for item in items]))
        > 1
    )


def add_trial_data_to_trial_handler(
    trial_data: TrialData, trial_handler: TrialHandlerExt
) -> None:
    for name, value in vars(trial_data).items():
        dtype = object if _contains_mixed_length_numpy_arrays(value) else None
        trial_handler.addData(name, np.array(value, dtype=dtype))


class MotorTask:
    def __init__(self, experiment: Experiment, win: Window | None = None):
        self.close_window_when_done = False
        self.experiment = experiment
        if win is None:
            win = Window(fullscr=True, units="height")
            self.close_window_when_done = True
        self.win = win
        if not experiment.trial_list:
            return
        self.trial_managers = {
            condition_index: TrialManager(self.win, trial)
            for condition_index, trial in enumerate(experiment.trial_list)
        }
        self.trial_handler = experiment.create_trialhandler()
        self.mouse = Mouse(visible=False, win=win)
        self.kb = Keyboard()
        self.js = joystick_wrapper.get_joystick()
        self.rng = np.random.default_rng()

    def run(self) -> bool:
        if not self.experiment.trial_list:
            return self._clean_up_and_return(False)
        try:
            self._do_trials()
            self.experiment.trial_handler_with_results = self.trial_handler
            self.experiment.stats = stats_dataframe(self.trial_handler)
            self.experiment.has_unsaved_changes = True
            return self._clean_up_and_return(True)
        except vis.MotorTaskCancelledByUser:
            return self._clean_up_and_return(False)
        except Exception as e:
            logging.warning(f"Run task failed with exception {e}")
            logging.exception(e)
            # clean up window before re-raising the exception
            if self.win is not None and self.close_window_when_done:
                self.win.close()
            raise

    def _do_trials(self) -> None:
        self._do_splash_screen()
        condition_trial_indices: list[list[int]] = [
            [] for _ in self.trial_handler.trialList
        ]
        current_condition_index = -1
        current_condition_first_trial_index = 0
        current_condition_clock = Clock()
        current_condition_max_time = 0.0
        self.mouse.setPos((0.0, 0.0))
        current_cursor_pos = (0.0, 0.0)
        for trial in self.trial_handler:
            if self.trial_handler.thisIndex != current_condition_index:
                # starting a new set of conditions
                current_condition_clock.reset()
                current_condition_max_time = trial["condition_timeout"]
                current_condition_index = self.trial_handler.thisIndex
                current_condition_first_trial_index = self.trial_handler.thisTrialN
                trial_manager = self.trial_managers[current_condition_index]
            condition_trial_indices[self.trial_handler.thisIndex].append(
                self.trial_handler.thisTrialN
            )
            if (
                current_condition_max_time <= 0.0
                or current_condition_clock.getTime() < current_condition_max_time
            ):
                # only do the trial if there is still time left for this condition
                current_cursor_pos = self._do_trial(
                    trial,
                    trial_manager,
                    current_cursor_pos,
                    current_condition_max_time - current_condition_clock.getTime(),
                )
            is_final_trial_of_block = (
                len(condition_trial_indices[self.trial_handler.thisIndex])
                == trial["weight"]
            )
            if is_final_trial_of_block and trial["post_block_delay"] > 0:
                vis.display_results(
                    trial["post_block_delay"],
                    trial["enter_to_skip_delay"],
                    trial["show_delay_countdown"],
                    self.trial_handler if trial["post_block_display_results"] else None,
                    self.experiment.display_options,
                    current_condition_first_trial_index,
                    True,
                    self.win,
                    self.mouse,
                    current_cursor_pos,
                )
        if self.win.nDroppedFrames > 0:
            logging.warning(f"Dropped {self.win.nDroppedFrames} frames")

    def _do_splash_screen(self) -> None:
        vis.splash_screen(
            display_time_seconds=self.experiment.metadata["display_duration"],
            enter_to_skip_delay=self.experiment.metadata["enter_to_skip_delay"],
            show_delay_countdown=self.experiment.metadata["show_delay_countdown"],
            metadata=self.experiment.metadata,
            win=self.win,
        )

    def _do_trial(
        self,
        trial: dict[str, Any],
        trial_manager: TrialManager,
        initial_cursor_pos: tuple[float, float],
        condition_timeout: float,
    ) -> tuple[float, float]:
        if trial["use_joystick"] and self.js is None:
            raise RuntimeError("Use joystick option is enabled, but no joystick found.")
        trial_manager.cursor.setPos(initial_cursor_pos)
        trial_manager.final_target_display_time_previous_trial = (
            trial_manager.most_recent_target_display_time
        )
        trial_data = TrialData(trial, self.rng)
        self.win.recordFrameIntervals = True
        trial_manager.clock.reset()
        vis.update_target_colors(
            trial_manager.targets, trial["show_inactive_targets"], None
        )
        if trial["show_target_labels"] and trial_manager.target_labels is not None:
            vis.update_target_label_colors(
                trial_manager.target_labels, trial["show_inactive_targets"], None
            )
        for index in trial_data.target_indices:
            if (
                condition_timeout <= 0.0
                or trial_manager.clock.getTime() < condition_timeout
            ):
                self._do_target(trial, index, trial_manager, trial_data)
        self.win.recordFrameIntervals = False
        if trial["automove_cursor_to_center"]:
            trial_data.to_center_success = [True] * trial["num_targets"]
        if (
            condition_timeout <= 0.0
            or trial_manager.clock.getTime() < condition_timeout
        ):
            # only store trial data if we didn't run out of time for this condition
            add_trial_data_to_trial_handler(trial_data, self.trial_handler)
        if trial["post_trial_delay"] > 0:
            vis.display_results(
                trial["post_trial_delay"],
                trial["enter_to_skip_delay"],
                trial["show_delay_countdown"],
                self.trial_handler if trial["post_trial_display_results"] else None,
                self.experiment.display_options,
                self.trial_handler.thisTrialN,
                False,
                self.win,
                self.mouse,
                trial_manager.cursor.pos,
            )
        return trial_manager.cursor.pos

    def _do_target(
        self, trial: dict[str, Any], index: int, tm: TrialManager, trial_data: TrialData
    ) -> None:
        minimum_window_for_flip = 1.0 / 60.0
        mouse_pos = tm.cursor.pos
        stop_waiting_time = 0.0
        stop_target_time = 0.0
        if trial["fixed_target_intervals"]:
            num_completed_targets = len(trial_data.to_target_timestamps)
            stop_waiting_time = (num_completed_targets + 1) * trial[
                "target_duration"
            ] - tm.final_target_display_time_previous_trial
            stop_target_time = stop_waiting_time + trial["target_duration"]
        for target_index in _get_target_indices(index, trial):
            t0 = tm.clock.getTime()
            is_central_target = target_index == trial["num_targets"]
            mouse_times = []
            mouse_positions = []

            # current target is not yet displayed
            if not is_central_target:
                if trial["automove_cursor_to_center"]:
                    mouse_pos = np.array([0.0, 0.0])
                    self.mouse.setPos(mouse_pos)
                    tm.cursor.setPos(mouse_pos)
                tm.cursor_path_add_vertex(mouse_pos, clear_existing=True)
            if not trial["fixed_target_intervals"]:
                if is_central_target:
                    pre_target_delay = trial["pre_central_target_delay"]
                else:
                    pre_target_delay = trial["pre_target_delay"]
                    if (
                        not tm.first_target_of_condition_shown
                        and trial["pre_first_target_extra_delay"] > 0
                    ):
                        pre_target_delay += trial["pre_first_target_extra_delay"]
                        tm.first_target_of_condition_shown = True
                stop_waiting_time = t0 + pre_target_delay
            if stop_waiting_time >= t0:
                if trial["hide_target_when_reached"]:
                    vis.update_target_colors(
                        tm.targets,
                        trial["show_inactive_targets"],
                        None,
                        tm.green_target_index,
                    )
                    if trial["show_target_labels"] and tm.target_labels is not None:
                        vis.update_target_label_colors(
                            tm.target_labels, trial["show_inactive_targets"], None
                        )
                # ensure we get at least a single flip
                should_continue_waiting = True
                while should_continue_waiting:
                    if trial["freeze_cursor_between_targets"]:
                        self.mouse.setPos(mouse_pos)
                    vis.draw_and_flip(self.win, tm.drawables, self.kb)
                    if not trial["freeze_cursor_between_targets"]:
                        if trial["use_joystick"]:
                            mouse_pos = tm.joystick_point_updater(
                                mouse_pos,
                                (self.js.getX(), self.js.getY()),  # type: ignore
                            )
                        else:
                            mouse_pos = tm.point_rotator(self.mouse.getPos())
                    mouse_times.append(tm.clock.getTime())
                    mouse_positions.append(mouse_pos)
                    if trial["show_cursor"]:
                        tm.cursor.setPos(mouse_pos)
                    if trial["show_cursor_path"]:
                        tm.cursor_path_add_vertex(mouse_pos)
                    should_continue_waiting = (
                        tm.clock.getTime() + minimum_window_for_flip < stop_waiting_time
                    )
            # display current target
            t0 = tm.clock.getTime()
            vis.update_target_colors(
                tm.targets, trial["show_inactive_targets"], target_index
            )
            if trial["show_target_labels"] and tm.target_labels is not None:
                vis.update_target_label_colors(
                    tm.target_labels, trial["show_inactive_targets"], target_index
                )
            if trial["play_sound"]:
                Sound("A", secs=0.160, blockSize=1024, stereo=True).play()
            if is_central_target:
                trial_data.to_center_num_timestamps_before_visible.append(
                    len(mouse_times)
                )
            else:
                trial_data.target_pos.append(tm.targets.xys[target_index])
                trial_data.to_target_num_timestamps_before_visible.append(
                    len(mouse_times)
                )
            target_size = trial["target_size"]
            if is_central_target:
                target_size = trial["central_target_size"]
            if not trial["fixed_target_intervals"]:
                if is_central_target:
                    stop_target_time = t0 + trial["central_target_duration"]
                else:
                    stop_target_time = t0 + trial["target_duration"]
            dist_correct = 1.0
            # ensure we get at least one flip
            should_continue_target = True
            while should_continue_target:
                vis.draw_and_flip(self.win, tm.drawables, self.kb)
                if trial["use_joystick"]:
                    mouse_pos = tm.joystick_point_updater(
                        mouse_pos,
                        (self.js.getX(), self.js.getY()),  # type: ignore
                    )
                else:
                    mouse_pos = tm.point_rotator(self.mouse.getPos())
                if trial["show_cursor"]:
                    tm.cursor.setPos(mouse_pos)
                mouse_times.append(tm.clock.getTime())
                mouse_positions.append(mouse_pos)
                if trial["show_cursor_path"]:
                    tm.cursor_path_add_vertex(mouse_pos)
                dist_correct, dist_any = to_target_dists(
                    mouse_pos,
                    tm.targets.xys,
                    target_index,
                    trial["add_central_target"],
                )
                if trial["ignore_incorrect_targets"] or is_central_target:
                    dist = dist_correct
                else:
                    dist = dist_any
                should_continue_target = (
                    dist > target_size
                    and tm.clock.getTime() + minimum_window_for_flip < stop_target_time
                )
            tm.most_recent_target_display_time = tm.clock.getTime() - stop_waiting_time
            success = (
                dist_correct <= target_size
                and tm.clock.getTime() + minimum_window_for_flip < stop_target_time
            )
            # When the target is reached, turn the color to green
            if success and trial["turn_target_to_green_when_reached"]:
                tm.green_target_index = target_index
            if is_central_target:
                trial_data.to_center_success.append(success)
            else:
                trial_data.to_target_success.append(success)
            if is_central_target:
                trial_data.to_center_timestamps.append(np.array(mouse_times))
                trial_data.to_center_mouse_positions.append(np.array(mouse_positions))
            else:
                trial_data.to_target_timestamps.append(np.array(mouse_times))
                trial_data.to_target_mouse_positions.append(np.array(mouse_positions))

    def _clean_up_and_return(self, return_value: bool) -> bool:
        if self.win is not None and self.close_window_when_done:
            self.win.close()
        return return_value
