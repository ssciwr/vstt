from __future__ import annotations

from typing import Dict

import vstt


def default_display_options() -> vstt.vtypes.DisplayOptions:
    return {
        "to_target_paths": True,
        "to_center_paths": False,
        "targets": True,
        "central_target": True,
        "to_target_reaction_time": True,
        "to_center_reaction_time": False,
        "to_target_movement_time": True,
        "to_center_movement_time": False,
        "to_target_time": True,
        "to_center_time": False,
        "to_target_distance": True,
        "to_center_distance": False,
        "to_target_rmse": True,
        "to_center_rmse": False,
        "averages": True,
    }


def display_options_labels() -> Dict[str, str]:
    return {
        "to_target_paths": "Display cursor paths to target",
        "to_center_paths": "Display cursor paths back to center",
        "targets": "Display targets",
        "central_target": "Display central target",
        "to_target_reaction_time": "Statistic: reaction time to target",
        "to_center_reaction_time": "Statistic: reaction time to center",
        "to_target_movement_time": "Statistic: movement time to target",
        "to_center_movement_time": "Statistic: movement time to center",
        "to_target_time": "Statistic: total time to target",
        "to_center_time": "Statistic: total time to center",
        "to_target_distance": "Statistic: movement distance to target",
        "to_center_distance": "Statistic: movement distance to center",
        "to_target_rmse": "Statistic: RMSE movement to target",
        "to_center_rmse": "Statistic: RMSE movement to center",
        "averages": "Also show statistics averaged over all targets",
    }


def import_display_options(display_options_dict: dict) -> vstt.vtypes.DisplayOptions:
    return vstt.common.import_typed_dict(
        display_options_dict, default_display_options()
    )
