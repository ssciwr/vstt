import copy
from typing import Dict
from typing import List
from typing import Optional

import motor_task_prototype.common as mtpcommon
import numpy as np
from motor_task_prototype.types import MotorTaskTrial
from psychopy.gui import DlgFromDict


def describe_trial(trial: MotorTaskTrial) -> str:
    repeats = f"{trial['weight']} repeat{'s' if trial['weight'] > 1 else ''}"
    targets = f"target{'s' if trial['num_targets'] > 1 else ''}"
    return f"{repeats} of {trial['num_targets']} {trial['target_order']} {targets}"


def describe_trials(trials: List[MotorTaskTrial]) -> str:
    return "\n".join(["  - " + describe_trial(trial) for trial in trials])


def default_trial() -> MotorTaskTrial:
    return {
        "weight": 1,
        "num_targets": 8,
        "target_order": "clockwise",
        "target_indices": "0 1 2 3 4 5 6 7",
        "target_duration": 5.0,
        "inter_target_duration": 1.0,
        "target_distance": 0.4,
        "target_size": 0.04,
        "central_target_size": 0.02,
        "play_sound": True,
        "show_cursor": True,
        "show_cursor_path": True,
        "automove_cursor_to_center": True,
        "cursor_rotation_degrees": 0.0,
        "post_trial_delay": 0.0,
        "post_trial_display_results": False,
        "post_block_delay": 0.0,
        "post_block_display_results": True,
    }


def trial_labels() -> Dict:
    return {
        "weight": "Repetitions",
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
        "automove_cursor_to_center": "Automatically move cursor to center",
        "cursor_rotation_degrees": "Cursor rotation (degrees)",
        "post_trial_delay": "Delay between trials (secs)",
        "post_trial_display_results": "Display results after each trial",
        "post_block_delay": "Delay after last trial (secs)",
        "post_block_display_results": "Display results after this block",
    }


def get_trial_from_user(
    initial_trial: Optional[MotorTaskTrial] = None,
) -> Optional[MotorTaskTrial]:
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
    return trial


def import_trial(trial_dict: dict) -> MotorTaskTrial:
    return mtpcommon.import_typed_dict(trial_dict, default_trial())


def validate_trial(trial: MotorTaskTrial) -> MotorTaskTrial:
    # make any negative time durations zero
    for duration in [
        "target_duration",
        "inter_target_duration",
        "post_trial_delay",
        "post_block_delay",
    ]:
        if trial[duration] < 0.0:  # type: ignore
            trial[duration] = 0.0  # type: ignore
    if isinstance(trial["target_indices"], str):
        # convert string of target indices to a numpy array of ints
        trial["target_indices"] = np.fromstring(
            trial["target_indices"], dtype="int", sep=" "
        )
    if trial["target_order"] == "fixed":
        # clip indices to valid range
        trial["target_indices"] = np.clip(
            trial["target_indices"], 0, trial["num_targets"] - 1
        )
    else:
        # construct clockwise sequence
        trial["target_indices"] = np.array(range(trial["num_targets"]))
        if trial["target_order"] == "anti-clockwise":
            trial["target_indices"] = np.flip(trial["target_indices"])
        elif trial["target_order"] == "random":
            rng = np.random.default_rng()
            rng.shuffle(trial["target_indices"])
    return trial
