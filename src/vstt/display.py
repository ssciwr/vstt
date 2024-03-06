from __future__ import annotations

import vstt


def default_display_options() -> vstt.vtypes.DisplayOptions:
    return {
        "to_target_paths": True,
        "to_center_paths": True,
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
        "to_target_success": False,
        "to_center_success": False,
        "area": False,
        "normalized_area": False,
        "peak_velocity": False,
        "peak_acceleration": False,
        "to_target_spatial_error": False,
        "to_center_spatial_error": False,
        "movement_time_at_peak_velocity": False,
        "total_time_at_peak_velocity": False,
        "movement_distance_at_peak_velocity": False,
        "rmse_movement_at_peak_velocity": False,
        "averages": True,
    }


def display_options_labels() -> dict[str, str]:
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
        "to_target_success": "Statistic: successful movement to target",
        "to_center_success": "Statistic: successful movement to center",
        "area": "Statistic: the area formed by the paths connecting the target and the center",
        "normalized_area": "Statistic: (the area formed by paths) / (length of the paths)²",
        "peak_velocity": "Statistic: maximum velocity during cursor movement",
        "peak_acceleration": "Statistic: maximum acceleration during cursor movement",
        "to_target_spatial_error": "Statistic: distance from the movement end point to the target",
        "to_center_spatial_error": "Statistic: distance from the movement end point to the center",
        "movement_time_at_peak_velocity": "Statistic: movement time to the point at the peak velocity",
        "total_time_at_peak_velocity": "Statistic: total time to the point at the peak velocity",
        "movement_distance_at_peak_velocity": "Statistic: movement distance to the point at the peak velocity",
        "rmse_movement_at_peak_velocity": "Statistic: RMSE movement to the point at the peak velocity",
        "averages": "Also show statistics averaged over all targets",
    }


def import_display_options(display_options_dict: dict) -> vstt.vtypes.DisplayOptions:
    return vstt.common.import_typed_dict(
        display_options_dict, default_display_options()
    )
