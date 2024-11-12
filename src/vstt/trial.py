from __future__ import annotations

import copy
from typing import Any
from typing import Mapping

import numpy as np
from psychopy.gui.qtgui import DlgFromDict

from vstt.common import import_typed_dict
from vstt.vtypes import Trial


def describe_trial(trial: Trial) -> str:
    repeats = f"{trial['weight']} repeat{'s' if trial['weight'] > 1 else ''}"
    targets = f"target{'s' if trial['num_targets'] > 1 else ''}"
    if trial["condition_timeout"] > 0.0:
        repeats = f"up to {repeats}"
        targets = f"{targets} in {trial['condition_timeout']}s"
    return f"{repeats} of {trial['num_targets']} {trial['target_order']} {targets}"


def describe_trials(trials: list[Trial]) -> str:
    return "\n".join(["  - " + describe_trial(trial) for trial in trials])


def default_trial() -> Trial:
    return {
        "weight": 1,
        "condition_timeout": 0.0,
        "num_targets": 8,
        "target_order": "clockwise",
        "target_indices": "0 1 2 3 4 5 6 7",
        "add_central_target": True,
        "hide_target_when_reached": True,
        "turn_target_to_green_when_reached": False,
        "show_target_labels": False,
        "target_labels": "0 1 2 3 4 5 6 7",
        "fixed_target_intervals": False,
        "target_duration": 5.0,
        "central_target_duration": 5.0,
        "pre_target_delay": 0.0,
        "pre_central_target_delay": 0.0,
        "pre_first_target_extra_delay": 0.0,
        "target_distance": 0.4,
        "target_size": 0.04,
        "central_target_size": 0.02,
        "show_inactive_targets": True,
        "ignore_incorrect_targets": True,
        "play_sound": True,
        "use_joystick": False,
        "joystick_max_speed": 0.02,
        "show_cursor": True,
        "cursor_size": 0.02,
        "show_cursor_path": True,
        "automove_cursor_to_center": False,
        "freeze_cursor_between_targets": False,
        "cursor_rotation_degrees": 0.0,
        "post_trial_delay": 0.0,
        "post_trial_display_results": False,
        "post_block_delay": 10.0,
        "post_block_display_results": True,
        "show_delay_countdown": True,
        "enter_to_skip_delay": True,
    }


def trial_labels() -> dict:
    return {
        "weight": "Repetitions",
        "condition_timeout": "Maximum time, 0=unlimited (secs)",
        "num_targets": "Number of targets",
        "target_order": "Target order",
        "target_indices": "Target indices",
        "add_central_target": "Add a central target",
        "hide_target_when_reached": "Hide target when reached",
        "turn_target_to_green_when_reached": "Turn target to green when reached",
        "show_target_labels": "Display target labels",
        "target_labels": "Target labels",
        "fixed_target_intervals": "Fixed target display intervals",
        "target_duration": "Target display duration (secs)",
        "central_target_duration": "Central target display duration (secs)",
        "pre_target_delay": "Delay before outer target display (secs)",
        "pre_central_target_delay": "Delay before central target display (secs)",
        "pre_first_target_extra_delay": "Extra delay before first outer target of condition (secs)",
        "target_distance": "Distance to targets (screen height fraction)",
        "target_size": "Target size (screen height fraction)",
        "central_target_size": "Central target size (screen height fraction)",
        "show_inactive_targets": "Show inactive targets",
        "ignore_incorrect_targets": "Ignore cursor hitting incorrect target",
        "play_sound": "Play a sound on target display",
        "use_joystick": "Control the cursor using a joystick",
        "joystick_max_speed": "Maximum joystick speed (screen height fraction per frame)",
        "show_cursor": "Show cursor",
        "cursor_size": "Cursor size (screen height fraction)",
        "show_cursor_path": "Show cursor path",
        "automove_cursor_to_center": "Automatically move cursor to center",
        "freeze_cursor_between_targets": "Freeze cursor until target is displayed",
        "cursor_rotation_degrees": "Cursor rotation (degrees)",
        "post_trial_delay": "Delay between trials (secs)",
        "post_trial_display_results": "Display results after each trial",
        "post_block_delay": "Delay after last trial (secs)",
        "post_block_display_results": "Display combined results after last trial",
        "show_delay_countdown": "Display a countdown during delays",
        "enter_to_skip_delay": "Skip delay by pressing enter key",
    }


def get_trial_from_user(
    initial_trial: Trial | None = None,
) -> Trial | None:
    trial = copy.deepcopy(initial_trial) if initial_trial else default_trial()
    order_of_targets = [trial["target_order"]]
    for target_order in ["clockwise", "anti-clockwise", "random", "fixed"]:
        if target_order != order_of_targets[0]:
            order_of_targets.append(target_order)
    trial["target_order"] = order_of_targets
    dialog = DlgFromDict(
        trial, title="Trial conditions", labels=trial_labels(), sortKeys=False
    )
    if not dialog.OK:
        return None
    return import_and_validate_trial(trial)


def import_and_validate_trial(trial_or_dict: Mapping[str, Any]) -> Trial:
    trial = import_typed_dict(trial_or_dict, default_trial())
    # make any negative time durations zero
    for duration in [
        "condition_timeout",
        "target_duration",
        "central_target_duration",
        "pre_target_delay",
        "pre_central_target_delay",
        "pre_first_target_extra_delay",
        "post_trial_delay",
        "post_block_delay",
    ]:
        if trial[duration] < 0.0:  # type: ignore
            trial[duration] = 0.0  # type: ignore
    # convert string of target indices to a numpy array of ints
    target_indices = np.fromstring(trial["target_indices"], dtype="int", sep=" ")
    if trial["target_order"] == "fixed":
        # clip indices to valid range
        target_indices = np.clip(target_indices, 0, trial["num_targets"] - 1)
    else:
        # construct clockwise sequence
        target_indices = np.array(range(trial["num_targets"]))
        if trial["target_order"] == "anti-clockwise":
            target_indices = np.flip(target_indices)
        elif trial["target_order"] == "random":
            rng = np.random.default_rng()
            rng.shuffle(target_indices)
    # convert array of indices back to a string
    trial["target_indices"] = " ".join(f"{int(i)}" for i in target_indices)
    return trial
