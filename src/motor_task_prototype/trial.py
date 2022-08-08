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
        "cursor_rotation": float,
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
        "cursor_rotation": 0.0,
    }


def get_trial_from_psydat(filename: str) -> MotorTaskTrial:
    psydata = fromFile(filename)
    return psydata.trialList[0]


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
        "cursor_rotation": "Cursor rotation (degrees)",
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
    # convert cursor rotation degrees to radians
    trial["cursor_rotation"] = trial["cursor_rotation"] * (2.0 * np.pi / 360.0)
    # convert string of target indices to a numpy array of ints
    trial["target_indices"] = np.fromstring(
        trial["target_indices"], dtype="int", sep=" "
    )
    return trial


def save_trial_to_psydat(trial: TrialHandlerExt) -> None:
    filename = fileSaveDlg(
        prompt="Save trial conditions and results as psydat file",
        allowed="Psydat files (*.psydat)",
    )
    if filename is not None:
        trial.saveAsPickle(filename)


def validate_trial(trial: MotorTaskTrial) -> MotorTaskTrial:
    if trial["target_order"] == "fixed":
        # clip indices to valid range
        trial["target_indices"] = np.clip(
            trial["target_indices"], 0, trial["num_targets"] - 1
        )
        return trial
    # construct clockwise sequence
    trial["target_indices"] = np.array(range(trial["num_targets"]))
    if trial["target_order"] == "anti-clockwise":
        trial["target_indices"] = np.flip(trial["target_indices"])
    elif trial["target_order"] == "random":
        rng = np.random.default_rng()
        rng.shuffle(trial["target_indices"])
    print(trial["target_indices"])
    return trial
