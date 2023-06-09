from __future__ import annotations

import logging
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

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
from vstt import joystick_wrapper
from vstt import vis
from vstt.experiment import Experiment
from vstt.geom import JoystickPointUpdater
from vstt.geom import PointRotator
from vstt.geom import to_target_dists
from vstt.stats import stats_dataframe


def _get_target_indices(outer_target_index: int, trial: Dict[str, Any]) -> List[int]:
    # always include outer target index
    indices = [outer_target_index]
    if trial["add_central_target"] and not trial["automove_cursor_to_center"]:
        # add central target index
        indices.append(trial["num_targets"])
    return indices


class TrialData:
    """Stores the data from the trial that will be stored in the psychopy trial_handler"""

    def __init__(self, trial: Dict[str, Any], rng: np.random.Generator):
        self.target_indices = np.fromstring(
            trial["target_indices"], dtype="int", sep=" "
        )
        if trial["target_order"] == "random":
            rng.shuffle(self.target_indices)
        self.target_pos: List[np.ndarray] = []
        self.to_target_timestamps: List[np.ndarray] = []
        self.to_target_num_timestamps_before_visible: List[int] = []
        self.to_center_timestamps: List[np.ndarray] = []
        self.to_center_num_timestamps_before_visible: List[int] = []
        self.to_target_mouse_positions: List[np.ndarray] = []
        self.to_center_mouse_positions: List[np.ndarray] = []
        self.to_target_success: List[bool] = []
        self.to_center_success: List[bool] = []


class TrialManager:
    """Stores the drawable elements and other objects needed during a trial"""

    def __init__(self, win: Window, trial: Dict[str, Any], rng: np.random.Generator):
        self.data = TrialData(trial, rng)
        self.targets = vis.make_targets(
            win,
            trial["num_targets"],
            trial["target_distance"],
            trial["target_size"],
            trial["add_central_target"],
            trial["central_target_size"],
        )
        self.target_labels = vis.make_target_labels(
            win,
            trial["num_targets"],
            trial["target_distance"],
            trial["target_size"],
            trial["target_labels"],
        )
        self.drawables: List[Union[BaseVisualStim, ElementArrayStim]] = [self.targets]
        if trial["show_target_labels"]:
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
        self._cursor_path_vertices: List[Tuple[float, float]] = []
        self.clock = Clock()
        if trial["show_cursor_path"]:
            self.drawables.append(self._cursor_path)

    def cursor_path_add_vertex(
        self, vertex: Tuple[float, float], clear_existing: bool = False
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
    def __init__(self, experiment: Experiment, win: Optional[Window] = None):
        self.close_window_when_done = False
        self.experiment = experiment
        if win is None:
            win = Window(fullscr=True, units="height")
            self.close_window_when_done = True
        self.win = win
        if not experiment.trial_list:
            return
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
        condition_trial_indices: List[List[int]] = [
            [] for _ in self.trial_handler.trialList
        ]
        current_condition_index = -1
        current_condition_first_trial_index = 0
        current_condition_clock = Clock()
        current_condition_max_time = 0.0
        for trial in self.trial_handler:
            if self.trial_handler.thisIndex != current_condition_index:
                # starting a new set of conditions
                current_condition_clock.reset()
                current_condition_max_time = trial["condition_timeout"]
                current_condition_index = self.trial_handler.thisIndex
                current_condition_first_trial_index = self.trial_handler.thisTrialN
            condition_trial_indices[self.trial_handler.thisIndex].append(
                self.trial_handler.thisTrialN
            )
            if (
                current_condition_max_time == 0.0
                or current_condition_clock.getTime() < current_condition_max_time
            ):
                # only do the trial if there is still time left for this condition
                self._do_trial(trial)
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

    def _do_trial(self, trial: Dict[str, Any]) -> None:
        if trial["use_joystick"] and self.js is None:
            raise RuntimeError("Use joystick option is enabled, but no joystick found.")
        tm = TrialManager(self.win, trial, self.rng)
        self.mouse.setPos(tm.cursor.pos)
        self.win.recordFrameIntervals = True
        tm.clock.reset()
        vis.update_target_colors(tm.targets, trial["show_inactive_targets"], None)
        if trial["show_target_labels"]:
            vis.update_target_label_colors(
                tm.target_labels, trial["show_inactive_targets"], None
            )
        for index in tm.data.target_indices:
            self._do_target(trial, index, tm)
        self.win.recordFrameIntervals = False
        if trial["automove_cursor_to_center"]:
            tm.data.to_center_success = [True] * trial["num_targets"]
        add_trial_data_to_trial_handler(tm.data, self.trial_handler)
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
            )

    def _do_target(self, trial: Dict[str, Any], index: int, tm: TrialManager) -> None:
        minimum_window_for_flip = 1.0 / 60.0
        mouse_pos = tm.cursor.pos
        stop_waiting_time = 0.0
        stop_target_time = 0.0
        if trial["fixed_target_intervals"]:
            num_completed_targets = len(tm.data.to_target_timestamps)
            stop_waiting_time = (num_completed_targets + 1) * trial["target_duration"]
            stop_target_time = stop_waiting_time + trial["target_duration"]
        for target_index in _get_target_indices(index, trial):
            t0 = tm.clock.getTime()
            is_central_target = target_index == trial["num_targets"]
            mouse_times = []
            mouse_positions = []
            if not is_central_target:
                if trial["automove_cursor_to_center"]:
                    mouse_pos = np.array([0.0, 0.0])
                    self.mouse.setPos(mouse_pos)
                    tm.cursor.setPos(mouse_pos)
                tm.cursor_path_add_vertex(mouse_pos, clear_existing=True)
                if not trial["fixed_target_intervals"]:
                    stop_waiting_time = t0 + trial["inter_target_duration"]
                if stop_waiting_time > t0:
                    if trial["hide_target_when_reached"]:
                        vis.update_target_colors(
                            tm.targets, trial["show_inactive_targets"], None
                        )
                        if trial["show_target_labels"]:
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
                                    mouse_pos, (self.js.getX(), self.js.getY())  # type: ignore
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
                            tm.clock.getTime() + minimum_window_for_flip
                            < stop_waiting_time
                        )
            # display current target
            t0 = tm.clock.getTime()
            vis.update_target_colors(
                tm.targets, trial["show_inactive_targets"], target_index
            )
            if trial["show_target_labels"]:
                vis.update_target_label_colors(
                    tm.target_labels, trial["show_inactive_targets"], target_index
                )
            if trial["play_sound"]:
                Sound("A", secs=0.3, blockSize=1024, stereo=True).play()
            if is_central_target:
                tm.data.to_center_num_timestamps_before_visible.append(len(mouse_times))
            else:
                tm.data.target_pos.append(tm.targets.xys[target_index])
                tm.data.to_target_num_timestamps_before_visible.append(len(mouse_times))
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
                        mouse_pos, (self.js.getX(), self.js.getY())  # type: ignore
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
            success = (
                dist_correct <= target_size
                and tm.clock.getTime() + minimum_window_for_flip < stop_target_time
            )
            if is_central_target:
                tm.data.to_center_success.append(success)
            else:
                tm.data.to_target_success.append(success)
            if is_central_target:
                tm.data.to_center_timestamps.append(np.array(mouse_times))
                tm.data.to_center_mouse_positions.append(np.array(mouse_positions))
            else:
                tm.data.to_target_timestamps.append(np.array(mouse_times))
                tm.data.to_target_mouse_positions.append(np.array(mouse_positions))

    def _clean_up_and_return(self, return_value: bool) -> bool:
        if self.win is not None and self.close_window_when_done:
            self.win.close()
        return return_value
