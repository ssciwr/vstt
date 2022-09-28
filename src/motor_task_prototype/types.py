import sys
from typing import List
from typing import Union

import numpy as np

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class MotorTaskTrial(TypedDict):
    weight: int
    num_targets: int
    target_order: Union[str, List]
    target_indices: Union[np.ndarray, str]
    target_duration: float
    inter_target_duration: float
    target_distance: float
    target_size: float
    central_target_size: float
    play_sound: bool
    automove_cursor_to_center: bool
    show_cursor: bool
    show_cursor_path: bool
    cursor_rotation_degrees: float
    post_trial_delay: float
    post_trial_display_results: bool
    post_block_delay: float
    post_block_display_results: bool


class MotorTaskDisplayOptions(TypedDict):
    to_target_paths: bool
    to_center_paths: bool
    targets: bool
    central_target: bool
    to_target_reaction_time: bool
    to_center_reaction_time: bool
    to_target_time: bool
    to_center_time: bool
    to_target_distance: bool
    to_center_distance: bool
    to_target_rmse: bool
    to_center_rmse: bool
    averages: bool


class MotorTaskMetadata(TypedDict):
    name: str
    subject: str
    date: str
    author: str
    display_title: str
    display_text1: str
    display_text2: str
    display_text3: str
    display_text4: str
