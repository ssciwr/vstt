from __future__ import annotations

from typing import Any
from typing import List
from typing import Tuple
from typing import Union

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
    to_target_mouse_positions = np.stack(
        np.array(data["to_target_mouse_positions"][index][i_target])
    )  # type: ignore
    to_target_success = np.array(data["to_target_success"][index][i_target])
    to_center_success: Union[np.ndarray, bool]
    if (
        type(data["to_center_timestamps"][index]) is np.ndarray
        and i_target < data["to_center_timestamps"][index].shape[0]
    ):
        to_center_timestamps = np.array(data["to_center_timestamps"][index][i_target])
        to_center_mouse_positions = np.stack(
            np.array(data["to_center_mouse_positions"][index][i_target])
        )  # type: ignore
        to_center_success = np.array(data["to_center_success"][index][i_target])
    else:
        to_center_timestamps = np.array([])
        to_center_mouse_positions = np.array([])
        to_center_success = True
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


def append_stats_data_to_excel(df: pd.DataFrame, writer: Any, data_format: str) -> None:
    """
    data_format can be
    - "trial": one sheet of data exported per trial
    - "target: one sheet of data exported per target
    """
    if data_format not in ["trial", "target"]:
        raise RuntimeError(f"data_format '{data_format}' not supported")
    data_labels = [
        "to_target_timestamps",
        "to_target_mouse_positions",
        "to_center_timestamps",
        "to_center_mouse_positions",
    ]
    # first sheet: all statistics, exclude arrays of timestamp/position data
    # convert columns of xy values to x column and y column of floats
    df_stats = df.drop(columns=data_labels)
    for label in ["target_pos", "center_pos"]:
        column_as_2d_array = np.stack(df_stats[f"{label}"].to_numpy())
        df_stats[f"{label}_x"] = column_as_2d_array[:, 0]
        df_stats[f"{label}_y"] = column_as_2d_array[:, 1]
        df_stats = df_stats.drop(columns=[label])
    df_stats.to_excel(writer, sheet_name="statistics", index=False)
    # add timestamp/mouse position arrays
    if data_format == "target":
        # one sheet for each row (target) in df, with arrays of time/position data.
        # arrays transposed to columns, x-y pairs are split into two columns.
        # 6 columns:
        #   - to_target_timestamps (negative until target displayed)
        #   - to_center_timestamps (negative until target displayed)
        #   - to_target_mouse_positions_x
        #   - to_target_mouse_positions_y
        #   - to_center_mouse_positions_x
        #   - to_center_mouse_positions_y
        for row in df.itertuples():
            df_data = pd.concat(
                [
                    pd.DataFrame({label: getattr(row, label)})
                    for label in ["to_target_timestamps", "to_center_timestamps"]
                ],
                axis=1,
            )
            for label in ["to_target_mouse_positions", "to_center_mouse_positions"]:
                arr = getattr(row, label)
                if arr.shape[-1] > 0:
                    df_data = pd.concat(
                        [
                            df_data,
                            pd.DataFrame(
                                {f"{label}_x": arr[:, 0], f"{label}_y": arr[:, 1]}
                            ),
                        ],
                        axis=1,
                    )
            df_data.to_excel(writer, sheet_name=f"{row.Index}", index=False)
    else:
        # one sheet per trial: all targets for a trial are concatenated
        # 6 columns:
        #   - timestamps (start from zero, increases throughout the trial)
        #   - mouse_x
        #   - mouse_y
        #   - target_index (-1 if no target is currently displayed)
        #   - target_x (-1 if no target is currently displayed)
        #   - target_y (-1 if no target is currently displayed)
        for i_trial in df.i_trial.unique():
            t0 = 0.0
            times = np.array([])
            x_positions = np.array([])
            y_positions = np.array([])
            i_targets = np.array([], dtype=np.int64)
            x_targets = np.array([])
            y_targets = np.array([])
            for row in df.loc[df.i_trial == i_trial].itertuples():
                for dest in ["target", "center"]:
                    raw_times = getattr(row, f"to_{dest}_timestamps")
                    if raw_times.shape[-1] > 0:
                        times = np.append(times, raw_times - raw_times[0] + t0)
                        points = getattr(row, f"to_{dest}_mouse_positions")
                        x_positions = np.append(x_positions, points[:, 0])
                        y_positions = np.append(y_positions, points[:, 1])
                        # set target info for all timestamps
                        if dest == "center":
                            pos = (0.0, 0.0)
                            i_target = -1  # give center target the special index -1
                        else:
                            pos = row.target_pos
                            i_target = row.i_target
                        target_i = np.full_like(raw_times, i_target, dtype=np.int64)
                        target_x = np.full_like(raw_times, pos[0])
                        target_y = np.full_like(raw_times, pos[1])
                        # set these to -99 if no target is visible (i.e. raw time is negative)
                        target_i[raw_times < 0] = -99
                        target_x[raw_times < 0] = -99
                        target_y[raw_times < 0] = -99
                        i_targets = np.append(i_targets, target_i)
                        x_targets = np.append(x_targets, target_x)
                        y_targets = np.append(y_targets, target_y)
                        t0 = (
                            times[-1] + 1.0 / 60.0
                        )  # add a single window flip between targets (?)
            df_data = pd.DataFrame(
                {
                    "timestamps": times,
                    "mouse_positions_x": x_positions,
                    "mouse_positions_y": y_positions,
                    "i_target": i_targets,
                    "target_x": x_targets,
                    "target_y": y_targets,
                }
            )
            df_data.to_excel(writer, sheet_name=f"{i_trial}", index=False)


def _reaction_time(
    mouse_times: np.ndarray,
    mouse_positions: np.ndarray,
    epsilon: float = 1e-12,
) -> float:
    if mouse_times.shape[0] != mouse_positions.shape[0] or mouse_times.shape[0] == 0:
        return np.nan
    i = 0
    while xydist(mouse_positions[0], mouse_positions[i]) < epsilon and i + 1 < len(
        mouse_times
    ):
        i += 1
    return mouse_times[i]


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
