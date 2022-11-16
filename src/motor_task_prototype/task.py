from __future__ import annotations

import logging
from typing import List
from typing import Optional
from typing import Union

import numpy as np
from motor_task_prototype import vis as mtpvis
from motor_task_prototype.experiment import MotorTaskExperiment
from motor_task_prototype.geom import PointRotator
from psychopy.clock import Clock
from psychopy.event import Mouse
from psychopy.event import xydist
from psychopy.hardware.keyboard import Keyboard
from psychopy.sound import Sound
from psychopy.visual.basevisual import BaseVisualStim
from psychopy.visual.elementarray import ElementArrayStim
from psychopy.visual.shape import ShapeStim
from psychopy.visual.window import Window


def run_task(
    experiment: MotorTaskExperiment,
    win: Optional[Window] = None,
    win_type: str = "pyglet",
) -> bool:
    def _clean_up_and_return(
        write_results_to_experiment: bool = False,
    ) -> bool:
        if win is not None and close_window_when_done:
            win.close()
        if write_results_to_experiment:
            experiment.trial_handler_with_results = trial_handler
            experiment.has_unsaved_changes = True
        return write_results_to_experiment

    close_window_when_done = False
    if not experiment.trial_list:
        return _clean_up_and_return()
    trial_handler = experiment.create_trialhandler()
    if win is None:
        win = Window(fullscr=True, units="height", winType=win_type)
        close_window_when_done = True
    mouse = Mouse(visible=False, win=win)
    clock = Clock()
    kb = Keyboard()
    mtpvis.splash_screen(experiment.metadata, win)
    condition_trial_indices: List[List[int]] = [[] for _ in trial_handler.trialList]
    rng = np.random.default_rng()
    for trial in trial_handler:
        targets: ElementArrayStim = mtpvis.make_targets(
            win,
            trial["num_targets"],
            trial["target_distance"],
            trial["target_size"],
            trial["central_target_size"],
        )
        drawables: List[Union[BaseVisualStim, ElementArrayStim]] = [targets]
        cursor = mtpvis.make_cursor(win, trial["cursor_size"])
        if trial["show_cursor"]:
            drawables.append(cursor)
        point_rotator = PointRotator(trial["cursor_rotation_degrees"])
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
        post_trial_delay = trial["post_trial_delay"]
        if is_final_trial_of_block:
            post_trial_delay = trial["post_block_delay"]
        trial_target_pos = []
        trial_to_target_timestamps = []
        trial_to_center_timestamps = []
        trial_to_target_mouse_positions = []
        trial_to_center_mouse_positions = []
        mouse_pos = (0.0, 0.0)
        target_indices = np.fromstring(trial["target_indices"], dtype="int", sep=" ")
        if trial["target_order"] == "random":
            rng.shuffle(target_indices)
        for index in target_indices:
            indices = [index]
            if not trial["automove_cursor_to_center"]:
                indices.append(trial["num_targets"])
            for target_index in indices:
                mtpvis.update_target_colors(
                    targets, trial["show_inactive_targets"], None
                )
                is_central_target = target_index == trial["num_targets"]
                if is_central_target:
                    prev_cursor_path.vertices = cursor_path.vertices
                    cursor_path.vertices = [prev_cursor_path.vertices[-1]]
                else:
                    cursor_path.vertices = [(0, 0)]
                    prev_cursor_path.vertices = [(0, 0)]
                    mouse.setPos((0.0, 0.0))
                    cursor.setPos((0.0, 0.0))
                    if not mtpvis.draw_and_flip(win, drawables, kb):
                        return _clean_up_and_return()
                    clock.reset()
                    while clock.getTime() < trial["inter_target_duration"]:
                        if not mtpvis.draw_and_flip(win, drawables, kb):
                            return _clean_up_and_return()
                    mouse.setPos((0.0, 0.0))
                    mouse_pos = (0.0, 0.0)
                mtpvis.update_target_colors(
                    targets, trial["show_inactive_targets"], target_index
                )
                if trial["play_sound"]:
                    Sound("A", secs=0.3, blockSize=512).play()
                if not is_central_target:
                    trial_target_pos.append(targets.xys[target_index])
                dist = xydist(mouse_pos, targets.xys[target_index])
                mouse_times = [0]
                mouse_positions = [mouse_pos]
                if not mtpvis.draw_and_flip(win, drawables, kb):
                    return _clean_up_and_return()
                clock.reset()
                win.recordFrameIntervals = True
                target_size = trial["target_size"]
                if is_central_target:
                    target_size = trial["central_target_size"]
                while dist > target_size and clock.getTime() < trial["target_duration"]:
                    mouse_pos = point_rotator(mouse.getPos())
                    if trial["show_cursor"]:
                        cursor.setPos(mouse_pos)
                    mouse_times.append(clock.getTime())
                    mouse_positions.append(mouse_pos)
                    if trial["show_cursor_path"]:
                        cursor_path.vertices = mouse_positions
                    dist = xydist(mouse_pos, targets.xys[target_index])
                    if not mtpvis.draw_and_flip(win, drawables, kb):
                        return _clean_up_and_return()
                win.recordFrameIntervals = False
                if is_central_target:
                    trial_to_center_timestamps.append(np.array(mouse_times))
                    trial_to_center_mouse_positions.append(np.array(mouse_positions))
                else:
                    trial_to_target_timestamps.append(np.array(mouse_times))
                    trial_to_target_mouse_positions.append(np.array(mouse_positions))
        trial_handler.addData("target_indices", np.array(target_indices))
        trial_handler.addData("target_pos", np.array(trial_target_pos))
        trial_handler.addData(
            "to_target_timestamps", np.array(trial_to_target_timestamps)
        )
        trial_handler.addData(
            "to_target_mouse_positions", np.array(trial_to_target_mouse_positions)
        )
        trial_handler.addData(
            "to_center_timestamps", np.array(trial_to_center_timestamps)
        )
        trial_handler.addData(
            "to_center_mouse_positions", np.array(trial_to_center_mouse_positions)
        )
        clock.reset()
        while clock.getTime() < post_trial_delay:
            if not mtpvis.draw_and_flip(win, [], kb):
                return _clean_up_and_return()
        n_trials_currently_in_block = len(
            condition_trial_indices[trial_handler.thisIndex]
        )
        display_trial_results = trial["post_trial_display_results"] or (
            is_final_trial_of_block
            and trial["post_block_display_results"]
            and n_trials_currently_in_block == 1
        )
        display_block_results = (
            is_final_trial_of_block
            and trial["post_block_display_results"]
            and n_trials_currently_in_block > 1
        )
        if display_trial_results:
            mtpvis.display_results(
                trial_handler,
                experiment.display_options,
                [trial_handler.thisTrialN],
                win,
            )
        if display_block_results:
            mtpvis.display_results(
                trial_handler,
                experiment.display_options,
                condition_trial_indices[trial_handler.thisIndex],
                win,
            )
    if win.nDroppedFrames > 0:
        logging.warning(f"Dropped {win.nDroppedFrames} frames")
    return _clean_up_and_return(True)
