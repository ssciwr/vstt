from __future__ import annotations

import logging
from typing import Any
from typing import Dict
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
        "to_target_num_timestamps_before_visible",
        "center_pos",
        "to_center_timestamps",
        "to_center_mouse_positions",
        "to_center_success",
        "to_center_num_timestamps_before_visible",
    ]


def _get_dat(
    data: Dict, key: str, index: Tuple, i_target: int, default_value: Any
) -> Any:
    ar = data.get(key)
    if ar is None:
        logging.debug(
            f"Key '{key}' not found in data, using default value {default_value}"
        )
        return default_value
    try:
        return ar[index][i_target]
    except IndexError:
        logging.debug(
            f"Index error for key '{key}', index '{index}', i_target '{i_target}', using default value {default_value}"
        )
    return default_value


def _get_target_data(
    trial_handler: TrialHandlerExt, index: Tuple, i_target: int
) -> List:
    data = trial_handler.data
    condition_index = trial_handler.sequenceIndices[index]
    target_index = data["target_indices"][index][i_target]
    target_pos = np.array(data["target_pos"][index][i_target])
    center_pos = np.array([0.0, 0.0])
    to_target_timestamps = np.array(data["to_target_timestamps"][index][i_target])
    to_target_num_timestamps_before_visible = _get_dat(
        data, "to_target_num_timestamps_before_visible", index, i_target, 0
    )
    to_target_mouse_positions = np.stack(
        np.array(data["to_target_mouse_positions"][index][i_target])
    )  # type: ignore
    to_target_success = np.array(data["to_target_success"][index][i_target])
    to_center_success: Union[np.ndarray, bool]
    to_center_timestamps = np.array(
        _get_dat(data, "to_center_timestamps", index, i_target, [])
    )
    to_center_num_timestamps_before_visible = _get_dat(
        data, "to_center_num_timestamps_before_visible", index, i_target, 0
    )
    to_center_mouse_positions = np.array(
        _get_dat(data, "to_center_mouse_positions", index, i_target, [])
    )
    if to_center_mouse_positions.shape[0] > 0:
        to_center_mouse_positions = np.stack(to_center_mouse_positions)  # type: ignore
    to_center_success = np.array(
        _get_dat(data, "to_center_success", index, i_target, True)
    )
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
        to_target_num_timestamps_before_visible,
        center_pos,
        to_center_timestamps,
        to_center_mouse_positions,
        to_center_success,
        to_center_num_timestamps_before_visible,
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
                x[f"to_{destination}_num_timestamps_before_visible"],
            ),
            axis=1,
        )
        df[f"to_{destination}_time"] = df.apply(
            lambda x: _total_time(
                x[f"to_{destination}_timestamps"],
                x[f"to_{destination}_num_timestamps_before_visible"],
            ),
            axis=1,
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
        #   - to_target_timestamps
        #   - to_center_timestamps
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
        #   - target_index (-99 if no target is currently displayed)
        #   - target_x (-99 if no target is currently displayed)
        #   - target_y (-99 if no target is currently displayed)
        for i_trial in df.i_trial.unique():
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
                        times = np.append(times, raw_times)
                        points = getattr(row, f"to_{dest}_mouse_positions")
                        x_positions = np.append(x_positions, points[:, 0])
                        y_positions = np.append(y_positions, points[:, 1])
                        # set target info for all timestamps
                        if dest == "center":
                            pos = (0.0, 0.0)
                            i_target = -1  # give center target the special index -1
                            num_timestamps_before_target_visible = (
                                row.to_center_num_timestamps_before_visible
                            )
                        else:
                            pos = row.target_pos
                            i_target = row.i_target
                            num_timestamps_before_target_visible = (
                                row.to_target_num_timestamps_before_visible
                            )
                        target_i = np.full_like(raw_times, i_target, dtype=np.int64)
                        target_x = np.full_like(raw_times, pos[0])
                        target_y = np.full_like(raw_times, pos[1])
                        # if no target is visible use the special index -99
                        target_i[0:num_timestamps_before_target_visible] = -99
                        target_x[0:num_timestamps_before_target_visible] = -99
                        target_y[0:num_timestamps_before_target_visible] = -99
                        i_targets = np.append(i_targets, target_i)
                        x_targets = np.append(x_targets, target_x)
                        y_targets = np.append(y_targets, target_y)
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
    to_target_num_timestamps_before_visible: int,
    epsilon: float = 1e-12,
) -> float:
    """
    The reaction time is defined as the timestamp where the cursor first moves,
    minus the timestamp where the target becomes visible.
    This means the reaction time can be negative if the cursor is moved before
    the target is made visible.

    :param mouse_times: The array of timestamps
    :param mouse_positions: The array of mouse positions
    :param to_target_num_timestamps_before_visible: The index of the first timestamp where the target is visible
    :param epsilon: The minimum euclidean distance to qualify as moving the cursor
    :return: The reaction time
    """
    if (
        mouse_times.shape[0] != mouse_positions.shape[0]
        or mouse_times.shape[0] == 0
        or mouse_times.shape[0] < to_target_num_timestamps_before_visible
    ):
        return np.nan
    i = 0
    while xydist(mouse_positions[0], mouse_positions[i]) < epsilon and i + 1 < len(
        mouse_times
    ):
        i += 1
    return mouse_times[i] - mouse_times[to_target_num_timestamps_before_visible]


def _total_time(
    mouse_times: np.ndarray,
    to_target_num_timestamps_before_visible: int,
) -> float:
    """
    The time to target is defined as the final timestamp (corresponding either to the target being reached
    or a timeout) minus the timestamp where the target becomes visible.

    :param mouse_times: The array of timestamps
    :param to_target_num_timestamps_before_visible: The index of the first timestamp where the target is visible
    :return: The total time to target
    """
    if (
        mouse_times.shape[0] == 0
        or mouse_times.shape[0] < to_target_num_timestamps_before_visible
    ):
        return np.nan
    return mouse_times[-1] - mouse_times[to_target_num_timestamps_before_visible]


def _distance(mouse_positions: np.ndarray) -> float:
    """
    The euclidean point-to-point distance travelled by the cursor.

    :param mouse_positions: The array of mouse positions
    :return: The distance travelled.
    """
    dist = 0
    for i in range(mouse_positions.shape[0] - 1):
        dist += xydist(mouse_positions[i + 1], mouse_positions[i])
    return dist


def _rmse(mouse_positions: np.ndarray, target_position: np.ndarray) -> float:
    """
    The Root Mean Square Error (RMSE) of the perpendicular distance from each mouse point
    to the straight line that intersects the initial mouse location and the target.

    See: https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Line_defined_by_two_points.

    :param mouse_positions: The array of mouse positions
    :param target: The x,y coordinates of the target
    :return: The RMSE of the distance from the ideal trajectoty
    """
    if mouse_positions.shape[0] <= 1:
        return np.nan
    # use first mouse position as origin point, so exclude it from RMSE measure
    x1, y1 = mouse_positions[0]
    x2, y2 = target_position
    norm = np.power(x2 - x1, 2) + np.power(y2 - y1, 2)
    norm *= mouse_positions.shape[0] - 1
    sum_of_squares = 0
    for x0, y0 in mouse_positions[1:]:
        sum_of_squares += np.power((x2 - x1) * (y1 - y0) - (x1 - x0) * (y2 - y1), 2)
    return np.sqrt(sum_of_squares / norm)
