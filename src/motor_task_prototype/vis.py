import copy
import sys
from typing import List
from typing import Optional

import numpy as np
from motor_task_prototype import stat as mtpstat
from motor_task_prototype.geom import points_on_circle
from psychopy import core
from psychopy.clock import Clock
from psychopy.colors import colors
from psychopy.data import TrialHandlerExt
from psychopy.gui import DlgFromDict
from psychopy.hardware.keyboard import Keyboard
from psychopy.visual.basevisual import BaseVisualStim
from psychopy.visual.circle import Circle
from psychopy.visual.elementarray import ElementArrayStim
from psychopy.visual.shape import ShapeStim
from psychopy.visual.textbox2 import TextBox2
from psychopy.visual.window import Window

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

colors.pop("none")

MotorTaskDisplayOptions = TypedDict(
    "MotorTaskDisplayOptions",
    {
        "to_target_paths": bool,
        "to_center_paths": bool,
        "targets": bool,
        "central_target": bool,
        "to_target_reaction_time": bool,
        "to_center_reaction_time": bool,
        "to_target_time": bool,
        "to_center_time": bool,
        "to_target_distance": bool,
        "to_center_distance": bool,
        "to_target_rmse": bool,
        "to_center_rmse": bool,
        "averages": bool,
    },
)


def default_display_options() -> MotorTaskDisplayOptions:
    return {
        "to_target_paths": True,
        "to_center_paths": False,
        "targets": True,
        "central_target": True,
        "to_target_reaction_time": True,
        "to_center_reaction_time": False,
        "to_target_time": True,
        "to_center_time": False,
        "to_target_distance": True,
        "to_center_distance": False,
        "to_target_rmse": True,
        "to_center_rmse": False,
        "averages": True,
    }


def get_display_options_from_user(
    initial_display_options: MotorTaskDisplayOptions = None,
) -> MotorTaskDisplayOptions:
    if initial_display_options:
        display_options = copy.deepcopy(initial_display_options)
    else:
        display_options = default_display_options()
    labels = {
        "to_target_paths": "Display cursor paths to target",
        "to_center_paths": "Display cursor paths back to center",
        "targets": "Display targets",
        "central_target": "Display central target",
        "to_target_reaction_time": "Statistic: reaction time to target",
        "to_center_reaction_time": "Statistic: reaction time to center",
        "to_target_time": "Statistic: movement time to target",
        "to_center_time": "Statistic: movement time to center",
        "to_target_distance": "Statistic: movement distance to target",
        "to_center_distance": "Statistic: movement distance to center",
        "to_target_rmse": "Statistic: RMSE movement to target",
        "to_center_rmse": "Statistic: RMSE movement to center",
        "averages": "Also show statistics averaged over all targets",
    }
    dialog = DlgFromDict(
        display_options,
        title="Motor task display options",
        labels=labels,
        sortKeys=False,
    )
    if not dialog.OK:
        core.quit()
    return display_options


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
        sizes=[[2.0 * point_radius] * 2] * n_circles
        + [[2.0 * center_point_radius] * 2],
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


def make_txt(name: str, units: str, stat: np.ndarray, index: int = None) -> str:
    if index is None:
        av = np.mean(stat)
    else:
        av = np.mean(stat, axis=0)[index]
    return f"{name}: {av: .3f}{units}\n"


def make_stats_txt(
    display_options: MotorTaskDisplayOptions,
    stats: mtpstat.MotorTaskStats,
    i_target: int = None,
) -> str:
    txt_stats = ""
    if display_options["to_target_reaction_time"]:
        txt_stats += make_txt("Reaction", "s", stats.to_target_reaction_times, i_target)
    if display_options["to_target_time"]:
        txt_stats += make_txt("Movement", "s", stats.to_target_times, i_target)
    if display_options["to_target_distance"]:
        txt_stats += make_txt("Distance", "", stats.to_target_distances, i_target)
    if display_options["to_target_rmse"]:
        txt_stats += make_txt("RMSE", "", stats.to_target_rmses, i_target)
    if display_options["to_center_reaction_time"]:
        txt_stats += make_txt(
            "Reaction (to center)", "s", stats.to_center_reaction_times, i_target
        )
    if display_options["to_center_time"]:
        txt_stats += make_txt(
            "Movement (to center)", "s", stats.to_center_times, i_target
        )
    if display_options["to_center_distance"]:
        txt_stats += make_txt(
            "Distance (to center)", "", stats.to_center_distances, i_target
        )
    if display_options["to_center_rmse"]:
        txt_stats += make_txt("RMSE (to center)", "", stats.to_center_rmses, i_target)
    return txt_stats


def display_results(
    results: TrialHandlerExt,
    trial_indices: List[int] = None,
    win: Window = None,
    win_type: str = "pyglet",
) -> None:
    close_window_when_done = False
    if win is None:
        win = Window(fullscr=True, units="height", winType=win_type)
        close_window_when_done = True
    if not results.extraInfo:
        display_options = default_display_options()
    else:
        display_options = results.extraInfo.get(
            "display_options", default_display_options()
        )
    if trial_indices is None:
        # if not specified, default to show block from the first condition for now
        # todo: instead of this, should have a separate wrapper for calling this
        # when displaying results from existing experiments
        trial_indices = []
        index = 0
        # assuming a single repetition of experiment:
        i_rep = 0
        for condition_index in results.sequenceIndices:
            if condition_index[i_rep] == 0:
                trial_indices.append(index)
            index += 1
    win.flip()
    clock = Clock()
    kb = Keyboard()
    drawables: List[BaseVisualStim] = []
    assert len(trial_indices) >= 1, "At least one trial is needed to be displayed"
    # for now assume the experiment is only repeated once
    i_repeat = 0
    i_condition = results.sequenceIndices[trial_indices[0]][i_repeat]
    conditions = results.trialList[i_condition]
    targets = results.data["target_pos"][trial_indices[0]][i_repeat]
    # stats
    stats = mtpstat.MotorTaskStats(results, trial_indices)
    letter_height = 0.015
    for i_target, (color, target_pos) in enumerate(zip(colors, targets)):
        txt_stats = make_stats_txt(display_options, stats, i_target)
        if target_pos[0] > 0:
            text_pos = target_pos[0] + 0.18, target_pos[1]
        else:
            text_pos = target_pos[0] - 0.18, target_pos[1]
        n_lines = txt_stats.count("\n")
        if n_lines <= 4:
            letter_height = 0.03
        if n_lines <= 6:
            letter_height = 0.02
        if len(txt_stats) > 0:
            drawables.append(
                TextBox2(
                    win,
                    txt_stats,
                    pos=text_pos,
                    color=color,
                    alignment="center",
                    letterHeight=letter_height,
                )
            )
    # average stats
    if display_options["averages"]:
        txt_stats = "Averages:\n" + make_stats_txt(display_options, stats)
        drawables.append(
            TextBox2(
                win,
                txt_stats,
                anchor="top_left",
                pos=(-0.5 * win.size[0] / win.size[1], 0.5),
                color="black",
                alignment="top_left",
                letterHeight=letter_height,
            )
        )
    # central target
    if (
        display_options["central_target"]
        and not conditions["automove_cursor_to_center"]
    ):
        drawables.append(
            Circle(
                win,
                radius=conditions["central_target_size"],
                pos=(0.0, 0.0),
                fillColor=(0.1, 0.1, 0.1),
            )
        )
    # targets
    if display_options["targets"]:
        for color, target_pos in zip(colors, targets):
            drawables.append(
                Circle(
                    win,
                    radius=conditions["target_size"],
                    pos=target_pos,
                    fillColor=color,
                )
            )
    # paths
    for i_trial in trial_indices:
        assert (
            results.sequenceIndices[i_trial][i_repeat] == i_condition
        ), "Trials to display should all use the same conditions"
        trial_mouse_positions = results.data["to_target_mouse_positions"][i_trial][
            i_repeat
        ]
        trial_mouse_positions_back = results.data["to_center_mouse_positions"][i_trial][
            i_repeat
        ]
        # paths to center
        if (
            display_options["to_center_paths"]
            and not conditions["automove_cursor_to_center"]
        ):
            for color, mouse_positions_back in zip(colors, trial_mouse_positions_back):
                drawables.append(
                    ShapeStim(
                        win,
                        vertices=mouse_positions_back,
                        lineColor=color,
                        closeShape=False,
                        lineWidth=3,
                    )
                )
        # paths to target
        if display_options["to_target_paths"]:
            for color, mouse_positions in zip(colors, trial_mouse_positions):
                drawables.append(
                    ShapeStim(
                        win,
                        vertices=mouse_positions,
                        lineColor=color,
                        closeShape=False,
                        lineWidth=3,
                    )
                )
    drawables.append(
        TextBox2(
            win,
            "Press press Enter when you are ready to continue...",
            pos=(0, -0.48),
            color="navy",
            alignment="center",
            letterHeight=0.03,
        )
    )
    clock.reset()
    while clock.getTime() < 30:
        if kb.getKeys(["escape", "return"]):
            if close_window_when_done:
                win.close()
            return
        draw_and_flip(win, drawables)
    if close_window_when_done:
        win.close()
