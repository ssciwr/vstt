from typing import List
from typing import Optional

import numpy as np
from psychopy.clock import Clock
from psychopy.colors import colors
from psychopy.data import TrialHandlerExt
from psychopy.hardware.keyboard import Keyboard
from psychopy.visual.basevisual import BaseVisualStim
from psychopy.visual.circle import Circle
from psychopy.visual.elementarray import ElementArrayStim
from psychopy.visual.shape import ShapeStim
from psychopy.visual.textbox2 import TextBox2
from psychopy.visual.window import Window

colors.pop("none")

from psychopy import core
from motor_task_prototype.geom import points_on_circle
from motor_task_prototype import stat as mtpstat


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
        xys=points_on_circle(n_circles, radius, include_centre=True),
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


def draw_and_flip(
    win: Window, drawables: List[BaseVisualStim], kb: Optional[Keyboard] = None
) -> None:
    for drawable in drawables:
        drawable.draw()
    if kb is not None and kb.getKeys(["escape"]):
        core.quit()
    win.flip()


def display_results(win: Window, results: TrialHandlerExt) -> None:
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
        reac, move = mtpstat.reaction_movement_times(timestamps, mouse_positions)
        dist = mtpstat.distance(mouse_positions)
        rmse = mtpstat.rmse(mouse_positions, target_pos)
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
        if kb.getKeys(["escape"]):
            return
        draw_and_flip(win, drawables)
