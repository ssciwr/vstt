from __future__ import annotations

from typing import List
from typing import Optional

import motor_task_prototype.meta as mtpmeta
import motor_task_prototype.stat as mtpstat
import numpy as np
from motor_task_prototype.geom import points_on_circle
from motor_task_prototype.types import MotorTaskDisplayOptions
from psychopy.colors import colorNames
from psychopy.data import TrialHandlerExt
from psychopy.hardware.keyboard import Keyboard
from psychopy.visual.basevisual import BaseVisualStim
from psychopy.visual.circle import Circle
from psychopy.visual.elementarray import ElementArrayStim
from psychopy.visual.shape import ShapeStim
from psychopy.visual.textbox2 import TextBox2
from psychopy.visual.window import Window

colorNames.pop("none")
colors = list(colorNames.values())


def make_cursor(window: Window, cursor_size: float) -> ShapeStim:
    return ShapeStim(
        window,
        lineColor="black",
        pos=(0, 0),
        lineWidth=5,
        vertices=[
            (-cursor_size * 0.5, 0.00),
            (cursor_size * 0.5, 0.00),
            (0.00, 0.00),
            (0.00, -cursor_size * 0.5),
            (0.00, cursor_size * 0.5),
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


def update_target_colors(
    targets: ElementArrayStim, show_inactive_targets: bool, index: Optional[int] = None
) -> None:
    inactive_rgb = 0.0
    if show_inactive_targets:
        inactive_rgb = 0.1
    c = np.array([[inactive_rgb, inactive_rgb, inactive_rgb]] * targets.nElements)
    if index is not None:
        # make specified target red
        c[index][0] = 1
        c[index][1] = -1
        c[index][2] = -1
    targets.setColors(c, colorSpace="rgb")


def draw_and_flip(
    win: Window,
    drawables: List[BaseVisualStim],
    kb: Keyboard,
    kb_stop_key: str = "escape",
) -> bool:
    should_continue = True
    for drawable in drawables:
        drawable.draw()
    if kb.getKeys([kb_stop_key]):
        should_continue = False
    win.flip()
    return should_continue


def make_txt(
    name: str, units: str, stat: np.ndarray, index: Optional[int] = None
) -> str:
    if stat.shape[-1] == 0:
        # no data available for this statistic
        return ""
    if index is None:
        av = np.mean(stat)
    else:
        av = np.mean(stat, axis=0)[index]
    return f"{name}: {av: .3f}{units}\n"


def make_stats_txt(
    display_options: MotorTaskDisplayOptions,
    stats: mtpstat.MotorTaskStats,
    i_target: Optional[int] = None,
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


def make_drawables(
    trial_handler: TrialHandlerExt,
    display_options: MotorTaskDisplayOptions,
    trial_indices: List[int],
    win: Window,
) -> List[BaseVisualStim]:
    drawables: List[BaseVisualStim] = []
    drawables.append(
        TextBox2(
            win,
            "Press press Enter when you are ready to continue...",
            pos=(0, -0.47),
            color="navy",
            alignment="center",
            letterHeight=0.03,
        )
    )
    if len(trial_indices) == 0 or trial_handler is None:
        # no results to display
        return drawables
    # for now assume the experiment is only repeated once
    i_repeat = 0
    i_condition = trial_handler.sequenceIndices[trial_indices[0]][i_repeat]
    conditions = trial_handler.trialList[i_condition]
    targets = trial_handler.data["target_pos"][trial_indices[0]][i_repeat]
    target_indices = trial_handler.data["target_indices"][trial_indices[0]][i_repeat]
    drawables.append(
        TextBox2(
            win,
            f"Condition {i_condition}, trial{'s' if len(trial_indices) > 1 else ''} {trial_indices}",
            anchor="top_center",
            pos=(0, 0.5),
            color="black",
            alignment="top_center",
            letterHeight=0.02,
        )
    )
    # stats
    stats = mtpstat.MotorTaskStats(trial_handler, trial_indices)
    letter_height = 0.015
    for i_target, target_pos in zip(target_indices, targets):
        color = colors[i_target]
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
        for i_target, target_pos in zip(target_indices, targets):
            drawables.append(
                Circle(
                    win,
                    radius=conditions["target_size"],
                    pos=target_pos,
                    fillColor=colors[i_target],
                )
            )
    # paths
    for i_trial in trial_indices:
        assert (
            trial_handler.sequenceIndices[i_trial][i_repeat] == i_condition
        ), "Trials to display should all use the same conditions"
        target_indices = trial_handler.data["target_indices"][i_trial][i_repeat]
        trial_mouse_positions = trial_handler.data["to_target_mouse_positions"][
            i_trial
        ][i_repeat]
        trial_mouse_positions_back = trial_handler.data["to_center_mouse_positions"][
            i_trial
        ][i_repeat]
        # paths to center
        if (
            display_options["to_center_paths"]
            and not conditions["automove_cursor_to_center"]
        ):
            for target_index, mouse_positions_back in zip(
                target_indices, trial_mouse_positions_back
            ):
                drawables.append(
                    ShapeStim(
                        win,
                        vertices=mouse_positions_back,
                        lineColor=colors[target_index],
                        closeShape=False,
                        lineWidth=3,
                    )
                )
        # paths to target
        if display_options["to_target_paths"]:
            for target_index, mouse_positions in zip(
                target_indices, trial_mouse_positions
            ):
                drawables.append(
                    ShapeStim(
                        win,
                        vertices=mouse_positions,
                        lineColor=colors[target_index],
                        closeShape=False,
                        lineWidth=3,
                    )
                )
    return drawables


def display_results(
    trial_handler: TrialHandlerExt,
    display_options: MotorTaskDisplayOptions,
    trial_indices: List[int],
    win: Optional[Window] = None,
    win_type: str = "pyglet",
) -> None:
    close_window_when_done = False
    if win is None:
        win = Window(fullscr=True, units="height", winType=win_type)
        close_window_when_done = True
    win.flip()
    kb = Keyboard()
    drawables = make_drawables(trial_handler, display_options, trial_indices, win)
    kb.clearEvents()
    while True:
        if not draw_and_flip(win, drawables, kb, "return"):
            if close_window_when_done:
                win.close()
            return


def splash_screen(
    metadata: mtpmeta.MotorTaskMetadata,
    win: Optional[Window] = None,
    win_type: str = "pyglet",
) -> None:
    close_window_when_done = False
    if win is None:
        win = Window(fullscr=True, units="height", winType=win_type)
        close_window_when_done = True
    kb = Keyboard()
    drawables: List[BaseVisualStim] = []
    drawables.append(
        TextBox2(
            win,
            "Press press Enter when you are ready to continue...",
            pos=(0, -0.40),
            color="navy",
            alignment="center",
            letterHeight=0.03,
        )
    )
    drawables.append(
        TextBox2(
            win,
            metadata["display_title"],
            pos=(0, 0.40),
            size=(1, None),
            color="black",
            bold=True,
            alignment="center",
            letterHeight=0.06,
        )
    )
    main_text = "\n\n".join(
        [
            metadata["display_text1"],
            metadata["display_text2"],
            metadata["display_text3"],
            metadata["display_text4"],
        ]
    )
    drawables.append(
        TextBox2(
            win,
            main_text,
            size=(1, None),
            pos=(0, 0),
            color="black",
            alignment="left",
            letterHeight=0.03,
        )
    )
    kb.clearEvents()
    while True:
        if not draw_and_flip(win, drawables, kb, "return"):
            if close_window_when_done:
                win.close()
            return
