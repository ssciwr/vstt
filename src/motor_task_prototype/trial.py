import logging
import sys
from typing import List
from typing import Union

import numpy as np
from psychopy import core
from psychopy.data import TrialHandlerExt
from psychopy.gui import DlgFromDict
from psychopy.gui import fileSaveDlg
from psychopy.misc import fromFile

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

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
        "cursor_rotation_degrees": float,
        "post_trial_delay": float,
        "post_block_delay": float,
    },
)


def default_trial() -> MotorTaskTrial:
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
        "cursor_rotation_degrees": 0.0,
        "post_trial_delay": 0.0,
        "post_block_delay": 0.0,
    }


def get_trial_from_psydat(filename: str) -> MotorTaskTrial:
    psydata = fromFile(filename)
    return import_trial(psydata.trialList[0])


def get_trial_from_user(
    trial: MotorTaskTrial = None,
) -> MotorTaskTrial:
    if trial is None:
        trial = default_trial()
    labels = {
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
        "cursor_rotation_degrees": "Cursor rotation (degrees)",
        "post_trial_delay": "Delay between trials (secs)",
        "post_block_delay": "Delay after last trial (secs)",
    }
    order_of_targets = [trial["target_order"]]
    for target_order in ["clockwise", "anti-clockwise", "random", "fixed"]:
        if target_order != order_of_targets[0]:
            order_of_targets.append(target_order)
    trial["target_order"] = order_of_targets
    dialog = DlgFromDict(
        trial, title="Motor task settings", labels=labels, sortKeys=False
    )
    if not dialog.OK:
        core.quit()
    return trial


def save_trial_to_psydat(trial: TrialHandlerExt) -> None:
    filename = fileSaveDlg(
        prompt="Save trial conditions and results as psydat file",
        allowed="Psydat files (*.psydat)",
    )
    if filename is not None:
        trial.saveAsPickle(filename)


def import_trial(trial_dict: dict) -> MotorTaskTrial:
    # start with a default valid trial
    trial = default_trial()
    # import all valid keys from input_trial
    for key in trial:
        if key in trial_dict:
            trial[key] = trial_dict[key]  # type: ignore
        else:
            logging.warning(f"Key '{key}' missing from trial")
    for key in trial_dict:
        if key not in trial:
            logging.warning(f"Ignoring unknown key '{key}'")
    return trial


def validate_trial(trial: MotorTaskTrial) -> MotorTaskTrial:
    # make any negative time durations zero
    for duration in [
        "target_duration",
        "inter_target_duration",
        "post_trial_delay",
        "post_block_delay",
    ]:
        if trial[duration] < 0:  # type: ignore
            trial[duration] = 0  # type: ignore
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
