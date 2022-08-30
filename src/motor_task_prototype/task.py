import logging
from typing import List
from typing import Union

import numpy as np
from motor_task_prototype import vis as mtpvis
from motor_task_prototype.geom import PointRotator
from motor_task_prototype.trial import MotorTaskTrial
from motor_task_prototype.trial import validate_trial
from psychopy.clock import Clock
from psychopy.data import TrialHandlerExt
from psychopy.event import Mouse
from psychopy.event import xydist
from psychopy.hardware.keyboard import Keyboard
from psychopy.sound import Sound
from psychopy.visual.basevisual import BaseVisualStim
from psychopy.visual.elementarray import ElementArrayStim
from psychopy.visual.shape import ShapeStim
from psychopy.visual.window import Window


class MotorTask:
    trial_handler: TrialHandlerExt

    def __init__(self, trial: MotorTaskTrial):
        trial = validate_trial(trial)
        self.trial_handler = TrialHandlerExt(
            [trial], nReps=1, method="sequential", originPath=-1
        )

    def run(self, winType: str = "pyglet") -> TrialHandlerExt:
        win = Window(fullscr=True, units="height", winType=winType)
        mouse = Mouse(visible=False, win=win)
        clock = Clock()
        kb = Keyboard()
        trial_counts = np.zeros((len(self.trial_handler.trialList),), dtype=int)
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
            trial_counts[self.trial_handler.thisIndex] += 1
            post_trial_delay = trial["post_trial_delay"]
            if trial_counts[self.trial_handler.thisIndex] % trial["weight"] == 0:
                post_trial_delay = trial["post_block_delay"]
            trial_target_pos = []
            trial_timestamps = []
            trial_timestamps_back = []
            trial_mouse_positions = []
            trial_mouse_positions_back = []
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
                        cursor.setPos((0.0, 0.0))
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
                        trial_timestamps_back.append(np.array(mouse_times))
                        trial_mouse_positions_back.append(np.array(mouse_positions))
                    else:
                        trial_timestamps.append(np.array(mouse_times))
                        trial_mouse_positions.append(np.array(mouse_positions))
            self.trial_handler.addData("target_pos", np.array(trial_target_pos))
            self.trial_handler.addData("timestamps", np.array(trial_timestamps))
            self.trial_handler.addData(
                "mouse_positions", np.array(trial_mouse_positions)
            )
            self.trial_handler.addData(
                "timestamps_back", np.array(trial_timestamps_back)
            )
            self.trial_handler.addData(
                "mouse_positions_back", np.array(trial_mouse_positions_back)
            )
            clock.reset()
            while clock.getTime() < post_trial_delay:
                win.flip()
        if win.nDroppedFrames > 0:
            logging.warning(f"Dropped {win.nDroppedFrames} frames")
        mouse.setVisible(True)
        win.close()
        return self.trial_handler
