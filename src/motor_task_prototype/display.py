import copy
from typing import Dict
from typing import Optional

import motor_task_prototype.common as mtpcommon
from motor_task_prototype.types import MotorTaskDisplayOptions
from psychopy import core
from psychopy.gui import DlgFromDict


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


def display_options_labels() -> Dict:
    return {
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


def get_display_options_from_user(
    initial_display_options: Optional[MotorTaskDisplayOptions] = None,
) -> MotorTaskDisplayOptions:
    if initial_display_options:
        display_options = copy.deepcopy(initial_display_options)
    else:
        display_options = default_display_options()
    dialog = DlgFromDict(
        display_options,
        title="Motor task display options",
        labels=display_options_labels(),
        sortKeys=False,
    )
    if not dialog.OK:
        core.quit()
    return display_options


def import_display_options(display_options_dict: dict) -> MotorTaskDisplayOptions:
    return mtpcommon.import_typed_dict(display_options_dict, default_display_options())
