from __future__ import annotations

import logging
from typing import List
from typing import Optional
from typing import Union

import numpy as np
from motor_task_prototype import config as mtpconfig
from motor_task_prototype import joystick_wrapper
from motor_task_prototype import vis as mtpvis
from motor_task_prototype.experiment import MotorTaskExperiment
from motor_task_prototype.geom import JoystickPointUpdater
from motor_task_prototype.geom import PointRotator
from motor_task_prototype.geom import to_target_dists
from motor_task_prototype.stat import stats_dataframe
from psychopy.clock import Clock
from psychopy.event import Mouse
from psychopy.hardware.keyboard import Keyboard
from psychopy.sound import Sound
from psychopy.visual.basevisual import BaseVisualStim
from psychopy.visual.elementarray import ElementArrayStim
from psychopy.visual.shape import ShapeStim
from psychopy.visual.window import Window


def run_task(experiment: MotorTaskExperiment, win: Optional[Window] = None) -> bool:
    def _clean_up_and_return(
        write_results_to_experiment: bool = False,
    ) -> bool:
        if win is not None and close_window_when_done:
            win.close()
        if write_results_to_experiment:
            experiment.trial_handler_with_results = trial_handler
            experiment.stats = stats_dataframe(trial_handler)
            experiment.has_unsaved_changes = True
        return write_results_to_experiment

    close_window_when_done = False
    try:
        if not experiment.trial_list:
            return _clean_up_and_return()
        trial_handler = experiment.create_trialhandler()
        if win is None:
            win = Window(fullscr=True, units="height", winType=mtpconfig.win_type)
            close_window_when_done = True
        mouse = Mouse(visible=False, win=win)
        clock = Clock()
        kb = Keyboard()
        js = joystick_wrapper.get_joystick()
        mtpvis.splash_screen(
            display_time_seconds=experiment.metadata["display_duration"],
            enter_to_skip_delay=experiment.metadata["enter_to_skip_delay"],
            show_delay_countdown=experiment.metadata["show_delay_countdown"],
            metadata=experiment.metadata,
            win=win,
        )
        condition_trial_indices: List[List[int]] = [[] for _ in trial_handler.trialList]
        rng = np.random.default_rng()
        for trial in trial_handler:
            if trial["use_joystick"] and js is None:
                raise RuntimeError(
                    "Use joystick option is enabled, but no joystick found."
                )
            target_indices = np.fromstring(
                trial["target_indices"], dtype="int", sep=" "
            )
            if trial["target_order"] == "random":
                rng.shuffle(target_indices)
            targets: ElementArrayStim = mtpvis.make_targets(
                win,
                trial["num_targets"],
                trial["target_distance"],
                trial["target_size"],
                trial["central_target_size"],
            )
            target_labels = mtpvis.make_target_labels(
                win,
                trial["num_targets"],
                trial["target_distance"],
                trial["target_size"],
                trial["target_labels"],
            )
            drawables: List[Union[BaseVisualStim, ElementArrayStim]] = [targets]
            if trial["show_target_labels"]:
                drawables.extend(target_labels)
            cursor = mtpvis.make_cursor(win, trial["cursor_size"])
            if trial["show_cursor"]:
                drawables.append(cursor)
            point_rotator = PointRotator(trial["cursor_rotation_degrees"])
            joystick_point_updater = JoystickPointUpdater(
                trial["cursor_rotation_degrees"], trial["joystick_max_speed"], win.size
            )
            cursor_path = ShapeStim(
                win, vertices=[(0, 0)], lineColor="white", closeShape=False
            )
            prev_cursor_path = ShapeStim(
                win, vertices=[(0, 0)], lineColor="white", closeShape=False
            )
            if trial["show_cursor_path"]:
                drawables.append(cursor_path)
                drawables.append(prev_cursor_path)
            condition_trial_indices[trial_handler.thisIndex].append(
                trial_handler.thisTrialN
            )
            is_final_trial_of_block = (
                len(condition_trial_indices[trial_handler.thisIndex]) == trial["weight"]
            )
            trial_target_pos = []
            trial_to_target_timestamps = []
            trial_to_center_timestamps = []
            trial_to_target_mouse_positions = []
            trial_to_center_mouse_positions = []
            trial_to_target_success = []
            trial_to_center_success = []
            mouse_pos = np.array([0.0, 0.0])
            mouse.setPos(mouse_pos)
            cursor.setPos(mouse_pos)
            for index in target_indices:
                indices = [index]
                if not trial["automove_cursor_to_center"]:
                    indices.append(trial["num_targets"])
                for target_index in indices:
                    mtpvis.update_target_colors(
                        targets, trial["show_inactive_targets"], None
                    )
                    mouse_times = []
                    mouse_positions = []
                    if trial["show_target_labels"]:
                        mtpvis.update_target_label_colors(
                            target_labels, trial["show_inactive_targets"], None
                        )
                    is_central_target = target_index == trial["num_targets"]
                    if is_central_target:
                        mouse_times = [0]
                        mouse_positions = [cursor_path.vertices[-1]]
                        prev_cursor_path.vertices = cursor_path.vertices
                        cursor_path.vertices = mouse_positions
                    else:
                        if trial["automove_cursor_to_center"]:
                            mouse_pos = np.array([0.0, 0.0])
                            mouse.setPos(mouse_pos)
                            cursor.setPos(mouse_pos)
                        cursor_path.vertices = [mouse_pos]
                        prev_cursor_path.vertices = [(0, 0)]
                        clock.reset()
                        while clock.getTime() < trial["inter_target_duration"]:
                            if trial["freeze_cursor_between_targets"]:
                                mouse.setPos(mouse_pos)
                            else:
                                if trial["use_joystick"]:
                                    mouse_pos = joystick_point_updater(
                                        mouse_pos, (js.getX(), js.getY())  # type: ignore
                                    )
                                else:
                                    mouse_pos = point_rotator(mouse.getPos())
                            mouse_times.append(
                                clock.getTime() - trial["inter_target_duration"]
                            )
                            mouse_positions.append(mouse_pos)
                            if trial["show_cursor"]:
                                cursor.setPos(mouse_pos)
                            if trial["show_cursor_path"]:
                                cursor_path.vertices = mouse_positions
                            if not mtpvis.draw_and_flip(win, drawables, kb):
                                return _clean_up_and_return()
                    mtpvis.update_target_colors(
                        targets, trial["show_inactive_targets"], target_index
                    )
                    if trial["show_target_labels"]:
                        mtpvis.update_target_label_colors(
                            target_labels, trial["show_inactive_targets"], target_index
                        )
                    if trial["play_sound"]:
                        Sound("A", secs=0.3, blockSize=1024).play()
                    if not is_central_target:
                        trial_target_pos.append(targets.xys[target_index])
                    dist_correct, dist_any = to_target_dists(
                        mouse_pos, targets.xys, target_index
                    )
                    if trial["ignore_incorrect_targets"] or is_central_target:
                        dist = dist_correct
                    else:
                        dist = dist_any
                    clock.reset()
                    win.recordFrameIntervals = True
                    target_size = trial["target_size"]
                    if is_central_target:
                        target_size = trial["central_target_size"]
                    while (
                        dist > target_size
                        and clock.getTime() < trial["target_duration"]
                    ):
                        if trial["use_joystick"]:
                            mouse_pos = joystick_point_updater(
                                mouse_pos, (js.getX(), js.getY())  # type: ignore
                            )
                        else:
                            mouse_pos = point_rotator(mouse.getPos())
                        if trial["show_cursor"]:
                            cursor.setPos(mouse_pos)
                        mouse_times.append(clock.getTime())
                        mouse_positions.append(mouse_pos)
                        if trial["show_cursor_path"]:
                            cursor_path.vertices = mouse_positions
                        dist_correct, dist_any = to_target_dists(
                            mouse_pos, targets.xys, target_index
                        )
                        if trial["ignore_incorrect_targets"] or is_central_target:
                            dist = dist_correct
                        else:
                            dist = dist_any
                        if not mtpvis.draw_and_flip(win, drawables, kb):
                            return _clean_up_and_return()
                    success = (
                        dist_correct <= target_size
                        and clock.getTime() < trial["target_duration"]
                    )
                    if is_central_target:
                        trial_to_center_success.append(success)
                    else:
                        trial_to_target_success.append(success)
                    win.recordFrameIntervals = False
                    if is_central_target:
                        trial_to_center_timestamps.append(np.array(mouse_times))
                        trial_to_center_mouse_positions.append(
                            np.array(mouse_positions)
                        )
                    else:
                        trial_to_target_timestamps.append(np.array(mouse_times))
                        trial_to_target_mouse_positions.append(
                            np.array(mouse_positions)
                        )
            trial_handler.addData("target_indices", np.array(target_indices))
            trial_handler.addData("target_pos", np.array(trial_target_pos))
            trial_handler.addData(
                "to_target_timestamps",
                np.array(trial_to_target_timestamps, dtype=object),
            )
            trial_handler.addData(
                "to_target_mouse_positions",
                np.array(trial_to_target_mouse_positions, dtype=object),
            )
            trial_handler.addData(
                "to_target_success", np.array(trial_to_target_success)
            )
            trial_handler.addData(
                "to_center_timestamps",
                np.array(trial_to_center_timestamps, dtype=object),
            )
            trial_handler.addData(
                "to_center_mouse_positions",
                np.array(trial_to_center_mouse_positions, dtype=object),
            )
            if trial["automove_cursor_to_center"]:
                trial_to_center_success = [True] * trial["num_targets"]
            trial_handler.addData(
                "to_center_success", np.array(trial_to_center_success)
            )
            if trial["post_trial_delay"] > 0:
                mtpvis.display_results(
                    trial["post_trial_delay"],
                    trial["enter_to_skip_delay"],
                    trial["show_delay_countdown"],
                    trial_handler if trial["post_trial_display_results"] else None,
                    experiment.display_options,
                    trial_handler.thisTrialN,
                    False,
                    win,
                )
            if is_final_trial_of_block and trial["post_block_delay"] > 0:
                mtpvis.display_results(
                    trial["post_block_delay"],
                    trial["enter_to_skip_delay"],
                    trial["show_delay_countdown"],
                    trial_handler if trial["post_block_display_results"] else None,
                    experiment.display_options,
                    trial_handler.thisTrialN,
                    True,
                    win,
                )
        if win.nDroppedFrames > 0:
            logging.warning(f"Dropped {win.nDroppedFrames} frames")
    except Exception as e:
        logging.warning(f"Run task failed with exception {e}")
        logging.exception(e)
        # clean up window before re-raising the exception
        if win is not None and close_window_when_done:
            win.close()
        raise

    return _clean_up_and_return(True)
