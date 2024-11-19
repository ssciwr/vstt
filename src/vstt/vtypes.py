from __future__ import annotations

import sys

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class Trial(TypedDict):
    weight: int
    condition_timeout: float
    num_targets: int
    target_order: str | list
    target_indices: str
    add_central_target: bool
    hide_target_when_reached: bool
    turn_target_to_green_when_reached: bool
    show_target_labels: bool
    target_labels: str
    fixed_target_intervals: bool
    target_duration: float
    central_target_duration: float
    pre_target_delay: float
    pre_central_target_delay: float
    pre_first_target_extra_delay: float
    target_distance: float
    target_size: float
    central_target_size: float
    show_inactive_targets: bool
    ignore_incorrect_targets: bool
    play_sound: bool
    use_joystick: bool
    joystick_max_speed: float
    show_cursor: bool
    cursor_size: float
    show_cursor_path: bool
    automove_cursor_to_center: bool
    freeze_cursor_between_targets: bool
    cursor_rotation_degrees: float
    post_trial_delay: float
    post_trial_display_results: bool
    post_block_delay: float
    post_block_display_results: bool
    show_delay_countdown: bool
    enter_to_skip_delay: bool


class DisplayOptions(TypedDict):
    to_target_paths: bool
    to_center_paths: bool
    targets: bool
    central_target: bool
    to_target_reaction_time: bool
    to_center_reaction_time: bool
    to_target_movement_time: bool
    to_center_movement_time: bool
    to_target_time: bool
    to_center_time: bool
    to_target_distance: bool
    to_center_distance: bool
    to_target_rmse: bool
    to_center_rmse: bool
    to_target_success: bool
    to_center_success: bool
    averages: bool
    area: bool
    normalized_area: bool
    peak_velocity: bool
    peak_acceleration: bool
    to_target_spatial_error: bool
    to_center_spatial_error: bool
    movement_time_at_peak_velocity: bool
    total_time_at_peak_velocity: bool
    movement_distance_at_peak_velocity: bool
    rmse_movement_at_peak_velocity: bool


class Metadata(TypedDict):
    name: str
    subject: str
    date: str
    author: str
    display_title: str
    display_text1: str
    display_text2: str
    display_text3: str
    display_text4: str
    display_duration: float
    show_delay_countdown: bool
    enter_to_skip_delay: bool
