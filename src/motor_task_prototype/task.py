import logging
from typing import List
from typing import Optional
from typing import Union

import numpy as np
from motor_task_prototype import vis as mtpvis
from motor_task_prototype.geom import PointRotator
from motor_task_prototype.meta import MotorTaskMetadata
from motor_task_prototype.trial import MotorTaskTrial
from motor_task_prototype.trial import validate_trial
from psychopy.clock import Clock
from psychopy.data import TrialHandlerExt
from psychopy.event import Mouse
from psychopy.event import xydist
from psychopy.gui import fileSaveDlg
from psychopy.hardware.keyboard import Keyboard
from psychopy.sound import Sound
from psychopy.visual.basevisual import BaseVisualStim
from psychopy.visual.elementarray import ElementArrayStim
from psychopy.visual.shape import ShapeStim
from psychopy.visual.window import Window


def new_experiment_from_trialhandler(experiment: TrialHandlerExt) -> TrialHandlerExt:
    for trial in experiment.trialList:
        validate_trial(trial)
    return TrialHandlerExt(
        experiment.trialList,
        nReps=1,
        method=experiment.method,
        originPath=-1,
        extraInfo=experiment.extraInfo,
    )


def new_experiment_from_dicts(
    trials: List[MotorTaskTrial],
    display_options: mtpvis.MotorTaskDisplayOptions,
    metadata: MotorTaskMetadata,
) -> TrialHandlerExt:
    for trial in trials:
        validate_trial(trial)
    return TrialHandlerExt(
        trials,
        nReps=1,
        method="sequential",
        originPath=-1,
        extraInfo={"display_options": display_options, "metadata": metadata},
    )


def save_experiment(experiment: TrialHandlerExt) -> None:
    filename = fileSaveDlg(
        prompt="Save trial conditions and results as psydat file",
        allowed="Psydat files (*.psydat)",
    )
    if filename is not None:
        experiment.saveAsPickle(filename)


class MotorTask:
    trial_handler: TrialHandlerExt

    def __init__(self, experiment: TrialHandlerExt):
        self.trial_handler = experiment

    def run(
        self, win: Optional[Window] = None, win_type: str = "pyglet"
    ) -> TrialHandlerExt:
        close_window_when_done = False
        if win is None:
            win = Window(fullscr=True, units="height", winType=win_type)
            close_window_when_done = True
        mouse = Mouse(visible=False, win=win)
        clock = Clock()
        kb = Keyboard()
        mtpvis.splash_screen(self.trial_handler.extraInfo["metadata"], win)
        condition_trial_indices: List[List[int]] = [
            [] for _ in self.trial_handler.trialList
        ]
        for trial in self.trial_handler:
            targets: ElementArrayStim = mtpvis.make_targets(
                win,
                trial["num_targets"],
                trial["target_distance"],
                trial["target_size"],
                trial["central_target_size"],
            )
            drawables: List[Union[BaseVisualStim, ElementArrayStim]] = [targets]
            cursor = mtpvis.make_cursor(win)
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
            condition_trial_indices[self.trial_handler.thisIndex].append(
                self.trial_handler.thisTrialN
            )
            is_final_trial_of_block = (
                len(condition_trial_indices[self.trial_handler.thisIndex])
                == trial["weight"]
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
            for index in trial["target_indices"]:
                indices = [index]
                if not trial["automove_cursor_to_center"]:
                    indices.append(trial["num_targets"])
                for target_index in indices:
                    mtpvis.update_target_colors(targets, None)
                    if target_index != trial["num_targets"]:
                        cursor_path.vertices = [(0, 0)]
                        prev_cursor_path.vertices = [(0, 0)]
                        mouse.setPos((0.0, 0.0))
                        cursor.setPos((0.0, 0.0))
                        mtpvis.draw_and_flip(win, drawables, kb)
                        clock.reset()
                        while clock.getTime() < trial["inter_target_duration"]:
                            mtpvis.draw_and_flip(win, drawables, kb)
                        mouse.setPos((0.0, 0.0))
                        mouse_pos = (0.0, 0.0)
                    else:
                        prev_cursor_path.vertices = cursor_path.vertices
                        cursor_path.vertices = [prev_cursor_path.vertices[-1]]
                    mtpvis.update_target_colors(targets, target_index)
                    if trial["play_sound"]:
                        Sound("A", secs=0.3, blockSize=512).play()
                    if target_index != trial["num_targets"]:
                        trial_target_pos.append(targets.xys[target_index])
                    dist = xydist(mouse_pos, targets.xys[target_index])
                    mouse_times = [0]
                    mouse_positions = [mouse_pos]
                    mtpvis.draw_and_flip(win, drawables, kb)
                    clock.reset()
                    win.recordFrameIntervals = True
                    target_size = trial["target_size"]
                    if target_index == trial["num_targets"]:
                        target_size = trial["central_target_size"]
                    while (
                        dist > target_size
                        and clock.getTime() < trial["target_duration"]
                    ):
                        mouse_pos = point_rotator(mouse.getPos())
                        if trial["show_cursor"]:
                            cursor.setPos(mouse_pos)
                        mouse_times.append(clock.getTime())
                        mouse_positions.append(mouse_pos)
                        if trial["show_cursor_path"]:
                            cursor_path.vertices = mouse_positions
                        dist = xydist(mouse_pos, targets.xys[target_index])
                        mtpvis.draw_and_flip(win, drawables, kb)
                    win.recordFrameIntervals = False
                    if target_index == trial["num_targets"]:
                        trial_to_center_timestamps.append(np.array(mouse_times))
                        trial_to_center_mouse_positions.append(
                            np.array(mouse_positions)
                        )
                    else:
                        trial_to_target_timestamps.append(np.array(mouse_times))
                        trial_to_target_mouse_positions.append(
                            np.array(mouse_positions)
                        )
            self.trial_handler.addData("target_pos", np.array(trial_target_pos))
            self.trial_handler.addData(
                "to_target_timestamps", np.array(trial_to_target_timestamps)
            )
            self.trial_handler.addData(
                "to_target_mouse_positions", np.array(trial_to_target_mouse_positions)
            )
            self.trial_handler.addData(
                "to_center_timestamps", np.array(trial_to_center_timestamps)
            )
            self.trial_handler.addData(
                "to_center_mouse_positions", np.array(trial_to_center_mouse_positions)
            )
            clock.reset()
            while clock.getTime() < post_trial_delay:
                win.flip()
            n_trials_currently_in_block = len(
                condition_trial_indices[self.trial_handler.thisIndex]
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
                    self.trial_handler,
                    [self.trial_handler.thisIndex],
                    win,
                )
            if display_block_results:
                mtpvis.display_results(
                    self.trial_handler,
                    condition_trial_indices[self.trial_handler.thisIndex],
                    win,
                )
        if win.nDroppedFrames > 0:
            logging.warning(f"Dropped {win.nDroppedFrames} frames")
        if close_window_when_done:
            win.close()
        win.flip()
        return self.trial_handler
