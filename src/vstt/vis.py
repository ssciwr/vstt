from __future__ import annotations

from typing import List
from typing import Optional

import numpy as np
import pandas as pd
from psychopy.clock import Clock
from psychopy.colors import colorNames
from psychopy.data import TrialHandlerExt
from psychopy.hardware.keyboard import Keyboard
from psychopy.visual.basevisual import BaseVisualStim
from psychopy.visual.circle import Circle
from psychopy.visual.elementarray import ElementArrayStim
from psychopy.visual.shape import ShapeStim
from psychopy.visual.textbox2 import TextBox2
from psychopy.visual.window import Window
from vstt.geom import points_on_circle
from vstt.stats import list_dest_stat_label_units
from vstt.stats import stats_dataframe
from vstt.vtypes import DisplayOptions
from vstt.vtypes import Metadata

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
    add_central_target: bool,
    center_point_radius: float,
) -> ElementArrayStim:
    n_elements = n_circles + 1 if add_central_target else n_circles
    sizes = [[2.0 * point_radius] * 2] * n_circles
    if add_central_target:
        sizes = sizes + [[2.0 * center_point_radius] * 2]
    return ElementArrayStim(
        window,
        units="height",
        fieldShape="circle",
        nElements=n_elements,
        sizes=sizes,
        xys=points_on_circle(n_circles, radius, include_centre=add_central_target),
        elementTex=None,
        elementMask="circle",
    )


def make_target_labels(
    window: Window,
    n_circles: int,
    radius: float,
    point_radius: float,
    labels_string: str,
) -> List[TextBox2]:
    text_boxes: List[TextBox2] = []
    positions = points_on_circle(n_circles, radius, include_centre=False)
    labels = labels_string.strip().split(" ")
    for label, position in zip(
        labels,
        positions,
    ):
        text_boxes.append(
            TextBox2(
                window,
                label,
                anchor="center",
                pos=position,
                color="white",
                bold=True,
                alignment="center",
                letterHeight=1.25 * point_radius,
            )
        )
    return text_boxes


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


def update_target_label_colors(
    target_labels: List[TextBox2],
    show_inactive_targets: bool,
    index: Optional[int] = None,
) -> None:
    inactive_rgb = 0.0
    if show_inactive_targets:
        inactive_rgb = 0.3
    for target_index, target_label in enumerate(target_labels):
        if target_index == index:
            target_label.color = (1, 1, 1)
        else:
            target_label.color = (inactive_rgb, inactive_rgb, inactive_rgb)


class MotorTaskCancelledByUser(Exception):
    pass


def draw_and_flip(
    win: Window,
    drawables: List[BaseVisualStim],
    kb: Optional[Keyboard],
    kb_stop_key: str = "escape",
) -> None:
    for drawable in drawables:
        drawable.draw()
    win.flip()
    if kb is not None and kb.getKeys([kb_stop_key]):
        raise MotorTaskCancelledByUser


def _make_stats_txt(display_options: DisplayOptions, stats: pd.Series) -> str:
    txt_stats = ""
    for destination, stat_label_units in list_dest_stat_label_units():
        for stat, label, unit in stat_label_units:
            if display_options.get(stat, False):  # type: ignore
                txt_stats += f"{label} (to {destination}): {stats[stat]: .3f}{unit}\n"
    return txt_stats


def _make_stats_drawables(
    trial_handler: TrialHandlerExt,
    display_options: DisplayOptions,
    stats_df: pd.DataFrame,
    win: Window,
) -> List[BaseVisualStim]:
    drawables: List[BaseVisualStim] = []
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
    letter_height = 0.014
    # split target_pos pair into two scalars so they survive the groupby.mean()
    stats_df[["target_pos_x", "target_pos_y"]] = pd.DataFrame(
        stats_df.target_pos.tolist(), index=stats_df.index
    )
    for _, row in (
        stats_df.groupby("target_index", as_index=False)
        .mean(numeric_only=True)
        .iterrows()
    ):
        color = colors[int(np.rint(row.target_index))]
        txt_stats = _make_stats_txt(display_options, row)
        if row.target_pos_x > 0:
            text_pos = row.target_pos_x + 0.18, row.target_pos_y
        else:
            text_pos = row.target_pos_x - 0.18, row.target_pos_y
        n_lines = txt_stats.count("\n")
        if n_lines <= 4:
            letter_height = 0.028
        if n_lines <= 6:
            letter_height = 0.018
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
        txt_stats = "Averages:\n" + _make_stats_txt(
            display_options, stats_df.mean(numeric_only=True)
        )
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
    # paths to center
    if (
        display_options["to_center_paths"]
        and conditions["add_central_target"]
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
    display_time_seconds: float,
    enter_to_skip_delay: bool,
    show_delay_countdown: bool,
    trial_handler: Optional[TrialHandlerExt],
    display_options: DisplayOptions,
    i_trial: int,
    all_trials_for_this_condition: bool,
    win: Optional[Window] = None,
) -> None:
    close_window_when_done = False
    if win is None:
        win = _make_window()
        close_window_when_done = True
    drawables = []
    if trial_handler is not None:
        stats_df = stats_dataframe(trial_handler)
        if all_trials_for_this_condition:
            condition_index = stats_df.loc[
                stats_df.i_trial == i_trial
            ].condition_index.to_numpy()[0]
            stats_df = stats_df.loc[stats_df.condition_index == condition_index]
        else:
            stats_df = stats_df.loc[stats_df.i_trial == i_trial]
        drawables = _make_stats_drawables(trial_handler, display_options, stats_df, win)
    display_drawables(
        display_time_seconds,
        enter_to_skip_delay,
        show_delay_countdown,
        drawables,
        win,
        close_window_when_done,
    )


def _make_textbox_press_enter(win: Window) -> TextBox2:
    return TextBox2(
        win,
        "Please press Enter when you are ready to continue...",
        pos=(0, -0.47),
        color="navy",
        alignment="center",
        letterHeight=0.03,
    )


def _make_textbox_title(title: str, win: Window) -> TextBox2:
    return TextBox2(
        win,
        title,
        pos=(0, 0.40),
        size=(1, None),
        color="black",
        bold=True,
        alignment="center",
        letterHeight=0.06,
    )


def _make_textbox_main_text(text: str, win: Window) -> TextBox2:
    return TextBox2(
        win,
        text,
        size=(1, None),
        pos=(0, 0),
        color="black",
        alignment="left",
        letterHeight=0.03,
    )


def _make_textbox_countdown(text: str, win: Window) -> TextBox2:
    return TextBox2(
        win,
        text,
        size=(1, None),
        pos=(0, -0.3),
        color="black",
        alignment="center",
        letterHeight=0.2,
    )


def _make_window() -> Window:
    return Window(fullscr=True, units="height")


def display_drawables(
    display_time_seconds: float,
    enter_to_skip_delay: bool,
    show_delay_countdown: bool,
    drawables: List[BaseVisualStim],
    win: Window,
    close_window_when_done: bool,
) -> None:
    if drawables is None:
        drawables = []
    remaining_display_time = int(np.ceil(display_time_seconds))
    if enter_to_skip_delay:
        kb = Keyboard()
        kb.clearEvents()
        drawables.append(_make_textbox_press_enter(win))
    else:
        kb = None
    if show_delay_countdown:
        countdown_textbox = _make_textbox_countdown(f"{remaining_display_time}", win)
        drawables.append(countdown_textbox)
    clock = Clock()
    clock.reset()
    while clock.getTime() < display_time_seconds:
        if show_delay_countdown:
            new_remaining_display_time = int(
                np.ceil(display_time_seconds - clock.getTime())
            )
            if new_remaining_display_time < remaining_display_time:
                remaining_display_time = new_remaining_display_time
                countdown_textbox.text = f"{remaining_display_time}"
        try:
            draw_and_flip(win, drawables, kb, "return")
        except MotorTaskCancelledByUser:
            if close_window_when_done:
                win.close()
            return
    if close_window_when_done:
        win.close()
    return


def splash_screen(
    display_time_seconds: float,
    enter_to_skip_delay: bool,
    show_delay_countdown: bool,
    metadata: Metadata,
    win: Optional[Window] = None,
) -> None:
    close_window_when_done = False
    if win is None:
        win = _make_window()
        close_window_when_done = True
    drawables = [_make_textbox_title(metadata["display_title"], win)]
    main_text = "\n\n".join(
        [
            metadata["display_text1"],
            metadata["display_text2"],
            metadata["display_text3"],
            metadata["display_text4"],
        ]
    )
    drawables.append(_make_textbox_main_text(main_text, win))
    display_drawables(
        display_time_seconds,
        enter_to_skip_delay,
        show_delay_countdown,
        drawables,
        win,
        close_window_when_done,
    )
