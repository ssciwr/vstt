from __future__ import annotations

from typing import List
from typing import Tuple

import numpy as np
import pandas as pd
from psychopy.data import TrialHandlerExt
from psychopy.event import xydist


def list_dest_stat_label_units() -> List[Tuple[str, List[Tuple[str, str, str]]]]:
    list_dest_stats = []
    for destination in ["target", "center"]:
        stats = []
        for base_stat, label, unit in [
            ("reaction_time", "Reaction", "s"),
            ("movement_time", "Movement", "s"),
            ("time", "Time", "s"),
            ("distance", "Distance", ""),
            ("rmse", "RMSE", ""),
        ]:
            stats.append((f"to_{destination}_{base_stat}", label, unit))
        list_dest_stats.append((destination, stats))
    return list_dest_stats


def _get_trial_data_columns() -> List[str]:
    return [
        "i_trial",
        "i_rep",
        "i_target",
        "condition_index",
        "target_index",
        "target_pos",
        "to_target_timestamps",
        "to_target_mouse_positions",
        "to_target_success",
        "center_pos",
        "to_center_timestamps",
        "to_center_mouse_positions",
        "to_center_success",
    ]


def _get_target_data(
    trial_handler: TrialHandlerExt, index: Tuple, i_target: int
) -> List:
    data = trial_handler.data
    condition_index = trial_handler.sequenceIndices[index]
    target_index = data["target_indices"][index][i_target]
    target_pos = np.array(data["target_pos"][index][i_target])
    center_pos = np.array([0.0, 0.0])
    to_target_timestamps = np.array(data["to_target_timestamps"][index][i_target])
    to_target_mouse_positions = np.array(
        data["to_target_mouse_positions"][index][i_target]
    )
    to_target_success = np.array(data["to_target_success"][index][i_target])
    if (
        type(data["to_center_timestamps"][index]) is np.ndarray
        and i_target < data["to_center_timestamps"][index].shape[0]
    ):
        to_center_timestamps = np.array(data["to_center_timestamps"][index][i_target])
        to_center_mouse_positions = np.array(
            data["to_center_mouse_positions"][index][i_target]
        )
        to_center_success = np.array(data["to_center_success"][index][i_target])
    else:
        to_center_timestamps = np.array([])
        to_center_mouse_positions = np.array([])
        to_center_success = np.array([])
    return [
        index[0],
        index[1],
        i_target,
        condition_index,
        target_index,
        target_pos,
        to_target_timestamps,
        to_target_mouse_positions,
        to_target_success,
        center_pos,
        to_center_timestamps,
        to_center_mouse_positions,
        to_center_success,
    ]


def _data_df(trial_handler: TrialHandlerExt) -> pd.DataFrame:
    data = []
    for index in np.ndindex(trial_handler.sequenceIndices.shape):
        # trials that have not yet happened have a default string instead of an array in their data
        if type(trial_handler.data["target_indices"][index]) is np.ndarray:
            n_targets = trial_handler.data["target_indices"][index].shape[0]
            for i_target in range(n_targets):
                data.append(_get_target_data(trial_handler, index, i_target))
    return pd.DataFrame(data, columns=_get_trial_data_columns())


def stats_dataframe(trial_handler: TrialHandlerExt) -> pd.DataFrame:
    df = _data_df(trial_handler)
    for destination in ["target", "center"]:
        df[f"to_{destination}_distance"] = df[f"to_{destination}_mouse_positions"].map(
            _distance
        )
        df[f"to_{destination}_reaction_time"] = df.apply(
            lambda x: _reaction_time(
                x[f"to_{destination}_timestamps"],
                x[f"to_{destination}_mouse_positions"],
            ),
            axis=1,
        )
        df[f"to_{destination}_time"] = df[f"to_{destination}_timestamps"].map(
            lambda x: x[-1] if x.shape[0] > 0 else np.nan
        )
        df[f"to_{destination}_movement_time"] = (
            df[f"to_{destination}_time"] - df[f"to_{destination}_reaction_time"]
        )
        df[f"to_{destination}_rmse"] = df.apply(
            lambda x: _rmse(
                x[f"to_{destination}_mouse_positions"], x[f"{destination}_pos"]
            ),
            axis=1,
        )
    return df


def _reaction_time(
    mouse_times: np.ndarray,
    mouse_positions: np.ndarray,
    epsilon: float = 1e-12,
) -> float:
    if mouse_times.shape[0] != mouse_positions.shape[0] or mouse_times.shape[0] <= 1:
        return np.nan
    i = 1
    while xydist(mouse_positions[0], mouse_positions[i]) < epsilon and i + 1 < len(
        mouse_times
    ):
        i += 1
    return mouse_times[i] - mouse_times[1]


def _distance(mouse_positions: np.ndarray) -> float:
    dist = 0
    for i in range(mouse_positions.shape[0] - 1):
        dist += xydist(mouse_positions[i + 1], mouse_positions[i])
    return dist


def _rmse(mouse_positions: np.ndarray, target: np.ndarray) -> float:
    if mouse_positions.shape[0] <= 1:
        return np.nan
    # use first mouse position as origin point, so exclude it from RMSE measure
    x1, y1 = mouse_positions[0]
    x2, y2 = target
    norm = np.power(x2 - x1, 2) + np.power(y2 - y1, 2)
    norm *= mouse_positions.shape[0] - 1
    sum_of_squares = 0
    for x0, y0 in mouse_positions[1:]:
        sum_of_squares += np.power((x2 - x1) * (y1 - y0) - (x1 - x0) * (y2 - y1), 2)
    return np.sqrt(sum_of_squares / norm)
