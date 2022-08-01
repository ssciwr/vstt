from psychopy.gui import DlgFromDict
from psychopy.visual.window import Window
from psychopy.visual.circle import Circle
from psychopy.visual.elementarray import ElementArrayStim
from psychopy.visual.shape import BaseShapeStim, ShapeStim
from psychopy.visual.basevisual import BaseVisualStim
from psychopy.visual.textbox2 import TextBox2
from psychopy.colors import Color, colors

colors.pop("none")
from psychopy.sound import Sound
from psychopy.clock import Clock
from psychopy.data import TrialHandlerExt, importConditions
from psychopy import core
from psychopy.event import Mouse, xydist
from psychopy.hardware.keyboard import Keyboard
from typing import List, Tuple, Union
import sys

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

import numpy as np
from motor_task_prototype import geometry as mtpgeom
from motor_task_prototype import analysis as mtpanalysis


def make_cursor(window: Window) -> ShapeStim:
    return ShapeStim(
        window,
        lineColor="black",
        pos=(0, 0),
        lineWidth=5,
        vertices=[
            (-0.01, 0.00),
            (0.01, 0.00),
            (0.00, 0.00),
            (0.00, -0.01),
            (0.00, 0.01),
        ],
        closeShape=False,
    )


def make_targets(
    window: Window,
    n_circles: int,
    radius: float,
    point_radius: float,
    center_point_radius: float,
) -> ElementArrayStim:
    return ElementArrayStim(
        window,
        units="height",
        fieldShape="circle",
        nElements=n_circles + 1,
        sizes=[2.0 * point_radius] * n_circles + [2.0 * center_point_radius],
        xys=mtpgeom.points_on_circle(n_circles, radius, include_centre=True),
        elementTex=None,
        elementMask="circle",
    )


def update_target_colors(targets: ElementArrayStim, index: int = None) -> None:
    # make all targets grey
    c = np.array([[0.1, 0.1, 0.1]] * targets.nElements)
    if index is not None:
        # make specified target red
        c[index][0] = 1
        c[index][1] = -1
        c[index][2] = -1
    targets.setColors(c, colorSpace="rgb")


def draw_and_flip(win: Window, drawables: List[BaseVisualStim], kb: Keyboard) -> None:
    for drawable in drawables:
        drawable.draw()
    if kb.getKeys(["escape"]):
        core.quit()
    win.flip()


MotorTaskTrial = TypedDict(
    "MotorTaskTrial",
    {
        "weight": int,
        "num_targets": int,
        "target_order": Union[str, List],
        "target_indices": Union[np.ndarray, str],
        "target_duration": float,
        "inter_target_duration": float,
        "target_distance": float,
        "target_size": float,
        "central_target_size": float,
        "play_sound": bool,
        "show_cursor": bool,
        "show_cursor_path": bool,
        "cursor_rotation": float,
    },
)


def get_default_motor_task_trial() -> MotorTaskTrial:
    return {
        "weight": 1,
        "num_targets": 8,
        "target_order": "clockwise",
        "target_indices": "0 1 2 3 4 5 6 7",
        "target_duration": 5,
        "inter_target_duration": 1,
        "target_distance": 0.4,
        "target_size": 0.04,
        "central_target_size": 0.02,
        "play_sound": True,
        "show_cursor": True,
        "show_cursor_path": True,
        "cursor_rotation": 0.0,
    }


def get_settings_from_user(
    settings: MotorTaskTrial = None,
) -> MotorTaskTrial:
    if settings is None:
        settings = get_default_motor_task_trial()
    labels = {
        "weight": "Number of repetitions",
        "num_targets": "Number of targets",
        "target_order": "Target order",
        "target_indices": "Target indices",
        "target_duration": "Target display duration (secs)",
        "inter_target_duration": "Delay between targets (secs)",
        "target_distance": "Distance to targets (screen height fraction)",
        "target_size": "Target size (screen height fraction)",
        "central_target_size": "Central target size (screen height fraction)",
        "play_sound": "Play a sound on target display",
        "show_cursor": "Show cursor",
        "show_cursor_path": "Show cursor path",
        "cursor_rotation": "Cursor rotation (degrees)",
    }
    order_of_targets = [settings["target_order"]]
    for target_order in ["clockwise", "anti-clockwise", "random", "fixed"]:
        if target_order != order_of_targets[0]:
            order_of_targets.append(target_order)
    settings["target_order"] = order_of_targets
    dialog = DlgFromDict(
        settings, title="Motor task settings", labels=labels, sortKeys=False
    )
    if not dialog.OK:
        core.quit()
    # convert cursor rotation degrees to radians
    settings["cursor_rotation"] = settings["cursor_rotation"] * (2.0 * np.pi / 360.0)
    # convert string of target indices to a numpy array of ints
    settings["target_indices"] = np.fromstring(
        settings["target_indices"], dtype="int", sep=" "
    )
    return settings


def process_settings(settings: MotorTaskTrial) -> MotorTaskTrial:
    if settings["target_order"] == "fixed":
        # clip indices to valid range
        settings["target_indices"] = np.clip(
            settings["target_indices"], 0, settings["num_targets"] - 1
        )
        return settings
    # construct clockwise sequence
    settings["target_indices"] = np.array(range(settings["num_targets"]))
    if settings["target_order"] == "anti-clockwise":
        settings["target_indices"] = np.flip(settings["target_indices"])
    elif settings["target_order"] == "random":
        rng = np.random.default_rng()
        rng.shuffle(settings["target_indices"])
    print(settings["target_indices"])
    return settings


class MotorTask:
    trials: TrialHandlerExt

    def __init__(self, settings: MotorTaskTrial):
        settings = process_settings(settings)
        self.trials = TrialHandlerExt([settings], 1, originPath=-1)

    def run(self, win: Window) -> TrialHandlerExt:
        for trial in self.trials:
            mouse = Mouse(visible=False)
            clock = Clock()
            kb = Keyboard()
            targets: ElementArrayStim = make_targets(
                win,
                trial["num_targets"],
                trial["target_distance"],
                trial["target_size"],
                trial["central_target_size"],
            )
            drawables: List[Union[BaseVisualStim, ElementArrayStim]] = [targets]
            cursor = make_cursor(win)
            if trial["show_cursor"]:
                drawables.append(cursor)
            point_rotator = mtpgeom.PointRotator(trial["cursor_rotation"])
            cursor_path = ShapeStim(
                win, vertices=[(0, 0)], lineColor="white", closeShape=False
            )
            if trial["show_cursor_path"]:
                drawables.append(cursor_path)
            trial_target_pos = []
            trial_timestamps = []
            trial_mouse_positions = []
            for target_index in trial["target_indices"]:
                update_target_colors(targets, None)
                cursor_path.vertices = [(0, 0)]
                cursor.setPos((0.0, 0.0))
                clock.reset()
                while clock.getTime() < trial["inter_target_duration"]:
                    draw_and_flip(win, drawables, kb)
                update_target_colors(targets, target_index)
                if trial["play_sound"]:
                    Sound("A", secs=0.3, blockSize=512).play()
                mouse_pos = (0.0, 0.0)
                trial_target_pos.append(targets.xys[target_index])
                dist = xydist(mouse_pos, targets.xys[target_index])
                mouse_times = [0]
                mouse_positions = [mouse_pos]
                mouse.setPos(mouse_pos)
                draw_and_flip(win, drawables, kb)
                clock.reset()
                mouse.setPos(mouse_pos)
                win.recordFrameIntervals = True
                while (
                    dist > trial["target_size"]
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
                    draw_and_flip(win, drawables, kb)
                win.recordFrameIntervals = False
                trial_timestamps.append(np.array(mouse_times))
                trial_mouse_positions.append(np.array(mouse_positions))
            self.trials.addData("target_pos", np.array(trial_target_pos))
            self.trials.addData("timestamps", np.array(trial_timestamps))
            self.trials.addData("mouse_positions", np.array(trial_mouse_positions))
        if win.nDroppedFrames > 0:
            print(f"Warning: dropped {win.nDroppedFrames} frames")
        win.flip()
        return self.trials

    def display_results(self, win: Window, results: TrialHandlerExt) -> None:
        clock = Clock()
        kb = Keyboard()
        # for now just get the data from the first trial
        conditions = results.trialList[results.sequenceIndices[0][0]]
        trial_target_pos = results.data["target_pos"][0][0]
        trial_mouse_positions = results.data["mouse_positions"][0][0]
        trial_timestamps = results.data["timestamps"][0][0]
        drawables: List[BaseVisualStim] = []
        for color, target_pos, mouse_positions, timestamps in zip(
            colors, trial_target_pos, trial_mouse_positions, trial_timestamps
        ):
            drawables.append(
                Circle(
                    win,
                    radius=conditions["target_size"],
                    pos=target_pos,
                    fillColor=color,
                )
            )
            drawables.append(
                ShapeStim(
                    win,
                    vertices=mouse_positions,
                    lineColor=color,
                    closeShape=False,
                    lineWidth=3,
                )
            )
            reac, move = mtpanalysis.reaction_movement_times(
                timestamps, mouse_positions
            )
            dist = mtpanalysis.distance(mouse_positions)
            rmse = mtpanalysis.rmse(mouse_positions, target_pos)
            if target_pos[0] > 0:
                text_pos = target_pos[0] + 0.16, target_pos[1]
            else:
                text_pos = target_pos[0] - 0.16, target_pos[1]
            drawables.append(
                TextBox2(
                    win,
                    f"Reaction: {reac:.3f}s\nMovement: {move:.3f}s\nDistance: {dist:.3f}\nRMSE: {rmse:.3f}",
                    pos=text_pos,
                    color=color,
                    alignment="center",
                    letterHeight=0.02,
                )
            )
        clock.reset()
        while clock.getTime() < 30:
            draw_and_flip(win, drawables, kb)
