from __future__ import annotations

from typing import List
from typing import Optional

import motor_task_prototype.meta as mtpmeta
import motor_task_prototype.stat as mtpstat
import numpy as np
import pandas as pd
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


def make_stats_txt(display_options: MotorTaskDisplayOptions, stats: pd.Series) -> str:
    txt_stats = ""
    for destination, stat_label_units in mtpstat.list_dest_stat_label_units():
        for stat, label, unit in stat_label_units:
            if display_options.get(stat, False):  # type: ignore
                txt_stats += f"{label} (to {destination}): {stats[stat]: .3f}{unit}\n"
    return txt_stats


def make_drawables(
    trial_handler: TrialHandlerExt,
    display_options: MotorTaskDisplayOptions,
    stats_df: pd.DataFrame,
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
    if stats_df.shape[0] == 0:
        # no results to display
        return drawables
    i_condition = stats_df.iloc[0].condition_index
    conditions = trial_handler.trialList[i_condition]
    trial_indices = stats_df.i_trial.unique()
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
    letter_height = 0.015
    # split target_pos pair into two scalars so they survive the groupby.mean()
    stats_df[["target_pos_x", "target_pos_y"]] = pd.DataFrame(
        stats_df.target_pos.tolist(), index=stats_df.index
    )
    for _, row in stats_df.groupby("target_index", as_index=False).mean().iterrows():
        color = colors[int(np.rint(row.target_index))]
        txt_stats = make_stats_txt(display_options, row)
        if row.target_pos_x > 0:
            text_pos = row.target_pos_x + 0.18, row.target_pos_y
        else:
            text_pos = row.target_pos_x - 0.18, row.target_pos_y
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
        txt_stats = "Averages:\n" + make_stats_txt(display_options, stats_df.mean())
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
        for _, row in stats_df.loc[stats_df.i_trial == trial_indices[0]].iterrows():
            drawables.append(
                Circle(
                    win,
                    radius=conditions["target_size"],
                    pos=row.target_pos,
                    fillColor=colors[row.target_index],
                )
            )
    # paths
    # paths to center
    if (
        display_options["to_center_paths"]
        and not conditions["automove_cursor_to_center"]
    ):
        for _, row in stats_df.iterrows():
            drawables.append(
                ShapeStim(
                    win,
                    vertices=row.to_center_mouse_positions,
                    lineColor=colors[row.target_index],
                    closeShape=False,
                    lineWidth=3,
                )
            )
    # paths to target
    if display_options["to_target_paths"]:
        for _, row in stats_df.iterrows():
            drawables.append(
                ShapeStim(
                    win,
                    vertices=row.to_target_mouse_positions,
                    lineColor=colors[row.target_index],
                    closeShape=False,
                    lineWidth=3,
                )
            )
    return drawables


def display_results(
    trial_handler: TrialHandlerExt,
    display_options: MotorTaskDisplayOptions,
    i_trial: int,
    all_trials_for_this_condition: bool,
    win: Optional[Window] = None,
    win_type: str = "pyglet",
) -> None:
    close_window_when_done = False
    if win is None:
        win = Window(fullscr=True, units="height", winType=win_type)
        close_window_when_done = True
    win.flip()
    kb = Keyboard()
    stats_df = mtpstat.stats_dataframe(trial_handler)
    if all_trials_for_this_condition:
        condition_index = stats_df.loc[
            stats_df.i_trial == i_trial
        ].condition_index.to_numpy()[0]
        stats_df = stats_df.loc[stats_df.condition_index == condition_index]
    else:
        stats_df = stats_df.loc[stats_df.i_trial == i_trial]
    drawables = make_drawables(trial_handler, display_options, stats_df, win)
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
