from __future__ import annotations

import copy
from typing import Dict
from typing import List
from typing import Optional

import numpy as np
from psychopy.gui import DlgFromDict
from vstt.common import import_typed_dict
from vstt.types import Trial


def describe_trial(trial: Trial) -> str:
    repeats = f"{trial['weight']} repeat{'s' if trial['weight'] > 1 else ''}"
    targets = f"target{'s' if trial['num_targets'] > 1 else ''}"
    return f"{repeats} of {trial['num_targets']} {trial['target_order']} {targets}"


def describe_trials(trials: List[Trial]) -> str:
    return "\n".join(["  - " + describe_trial(trial) for trial in trials])


def default_trial() -> Trial:
    return {
        "weight": 1,
        "num_targets": 8,
        "target_order": "clockwise",
        "target_indices": "0 1 2 3 4 5 6 7",
        "add_central_target": True,
        "show_target_labels": False,
        "target_labels": "0 1 2 3 4 5 6 7",
        "fixed_target_intervals": False,
        "target_duration": 5.0,
        "inter_target_duration": 1.0,
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
        "automove_cursor_to_center": True,
        "freeze_cursor_between_targets": True,
        "cursor_rotation_degrees": 0.0,
        "post_trial_delay": 0.0,
        "post_trial_display_results": False,
        "post_block_delay": 5.0,
        "post_block_display_results": True,
        "show_delay_countdown": True,
        "enter_to_skip_delay": True,
    }


def trial_labels() -> Dict:
    return {
        "weight": "Repetitions",
        "num_targets": "Number of targets",
        "target_order": "Target order",
        "target_indices": "Target indices",
        "add_central_target": "Add a central target",
        "show_target_labels": "Display target labels",
        "target_labels": "Target labels",
        "fixed_target_intervals": "Fixed target display intervals",
        "target_duration": "Target display duration (secs)",
        "inter_target_duration": "Delay between targets (secs)",
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
        "post_block_display_results": "Display results after this block",
        "show_delay_countdown": "Display a countdown during delays",
        "enter_to_skip_delay": "Skip delay by pressing enter key",
    }


def get_trial_from_user(
    initial_trial: Optional[Trial] = None,
) -> Optional[Trial]:
    if initial_trial:
        trial = copy.deepcopy(initial_trial)
    else:
        trial = default_trial()
    order_of_targets = [trial["target_order"]]
    for target_order in ["clockwise", "anti-clockwise", "random", "fixed"]:
        if target_order != order_of_targets[0]:
            order_of_targets.append(target_order)
    trial["target_order"] = order_of_targets
    dialog = DlgFromDict(
        trial, title="Trial settings", labels=trial_labels(), sortKeys=False
    )
    if not dialog.OK:
        return None
    return validate_trial(trial)


def import_trial(trial_dict: dict) -> Trial:
    return import_typed_dict(trial_dict, default_trial())


def validate_trial(trial: Trial) -> Trial:
    # make any negative time durations zero
    for duration in [
        "target_duration",
        "inter_target_duration",
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
