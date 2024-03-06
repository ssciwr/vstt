from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from numpy import linalg as LA
from psychopy.data import TrialHandlerExt
from psychopy.event import xydist
from shapely.geometry import LineString
from shapely.ops import polygonize
from shapely.ops import unary_union

min_distance: float = 1e-12


def list_dest_stat_label_units() -> list[tuple[str, list[tuple[str, str, str]]]]:
    list_dest_stats = []
    for destination in ["target", "center"]:
        stats = []
        for base_stat, label, unit in [
            ("reaction_time", "Reaction", "s"),
            ("movement_time", "Movement", "s"),
            ("time", "Time", "s"),
            ("distance", "Distance", ""),
            ("rmse", "RMSE", ""),
            ("success", "Success", ""),
            ("spatial_error", "Spatial", ""),
        ]:
            stats.append((f"to_{destination}_{base_stat}", label, unit))
        list_dest_stats.append((destination, stats))
    list_dest_stats.append(("", [("area", "Area", "")]))
    list_dest_stats.append(("", [("normalized_area", "Normalized Area", "")]))
    list_dest_stats.append(("", [("peak_velocity", "Peak Velocity", "")]))
    list_dest_stats.append(("", [("peak_acceleration", "Peak Acceleration", "")]))
    list_dest_stats.append(
        (
            "",
            [("movement_time_at_peak_velocity", "Movement Time at Peak Velocity", "s")],
        )
    )
    list_dest_stats.append(
        ("", [("total_time_at_peak_velocity", "Total Time at Peak Velocity", "s")])
    )
    list_dest_stats.append(
        (
            "",
            [
                (
                    "movement_distance_at_peak_velocity",
                    "Movement Distance at Peak Velocity",
                    "",
                )
            ],
        )
    )
    list_dest_stats.append(
        ("", [("rmse_movement_at_peak_velocity", "RMSE Movement at Peak Velocity", "")])
    )
    return list_dest_stats


def _get_trial_data_columns() -> list[str]:
    return [
        "i_trial",
        "i_rep",
        "i_target",
        "condition_index",
        "target_index",
        "target_pos",
        "target_radius",
        "to_target_timestamps",
        "to_target_mouse_positions",
        "to_target_success",
        "to_target_num_timestamps_before_visible",
        "center_pos",
        "center_radius",
        "to_center_timestamps",
        "to_center_mouse_positions",
        "to_center_success",
        "to_center_num_timestamps_before_visible",
    ]


def _get_dat(
    data: dict, key: str, index: tuple, i_target: int, default_value: Any
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
    trial_handler: TrialHandlerExt, index: tuple, i_target: int
) -> list:
    data = trial_handler.data
    condition_index = trial_handler.sequenceIndices[index]
    conditions = trial_handler.trialList[condition_index]
    target_radius = conditions["target_size"]
    central_target_radius = conditions["central_target_size"]
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
    to_center_success: np.ndarray | bool
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
        target_radius,
        to_target_timestamps,
        to_target_mouse_positions,
        to_target_success,
        to_target_num_timestamps_before_visible,
        center_pos,
        central_target_radius,
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
            lambda x, destination=destination: _reaction_time(
                x[f"to_{destination}_timestamps"],
                x[f"to_{destination}_mouse_positions"],
                x[f"to_{destination}_num_timestamps_before_visible"],
            ),
            axis=1,
        )
        df[f"to_{destination}_time"] = df.apply(
            lambda x, destination=destination: _total_time(
                x[f"to_{destination}_timestamps"],
                x[f"to_{destination}_num_timestamps_before_visible"],
            ),
            axis=1,
        )
        df[f"to_{destination}_movement_time"] = (
            df[f"to_{destination}_time"] - df[f"to_{destination}_reaction_time"]
        )
        df[f"to_{destination}_rmse"] = df.apply(
            lambda x, destination=destination: _rmse(
                x[f"to_{destination}_mouse_positions"], x[f"{destination}_pos"]
            ),
            axis=1,
        )
        df[f"to_{destination}_spatial_error"] = df.apply(
            lambda x, destination=destination: _spatial_error(
                x[f"to_{destination}_mouse_positions"],
                x[f"{destination}_pos"],
                x[f"{destination}_radius"],
            ),
            axis=1,
        )
    df["area"] = df.apply(
        lambda x: _area(x["to_target_mouse_positions"], x["to_center_mouse_positions"]),
        axis=1,
    )
    df["normalized_area"] = df.apply(
        lambda x: _normalized_area(
            x["to_target_mouse_positions"], x["to_center_mouse_positions"]
        ),
        axis=1,
    )
    df["peak_velocity"] = df.apply(
        lambda x: _peak_velocity(
            np.concatenate((x["to_target_timestamps"], x["to_center_timestamps"])),
            concatenate_mouse_positions(x),
        )[0],
        axis=1,
    )
    df["peak_acceleration"] = df.apply(
        lambda x: _peak_acceleration(
            np.concatenate((x["to_target_timestamps"], x["to_center_timestamps"])),
            concatenate_mouse_positions(x),
        ),
        axis=1,
    )
    df["movement_time_at_peak_velocity"] = df.apply(
        lambda x: _movement_time_at_peak_velocity(
            np.concatenate((x["to_target_timestamps"], x["to_center_timestamps"])),
            concatenate_mouse_positions(x),
            x["to_target_num_timestamps_before_visible"],
        ),
        axis=1,
    )
    df["total_time_at_peak_velocity"] = df.apply(
        lambda x: _total_time_at_peak_velocity(
            np.concatenate((x["to_target_timestamps"], x["to_center_timestamps"])),
            concatenate_mouse_positions(x),
            x["to_target_num_timestamps_before_visible"],
        ),
        axis=1,
    )
    df["movement_distance_at_peak_velocity"] = df.apply(
        lambda x: _movement_distance_at_peak_velocity(
            np.concatenate((x["to_target_timestamps"], x["to_center_timestamps"])),
            concatenate_mouse_positions(x),
            x["to_target_num_timestamps_before_visible"],
        ),
        axis=1,
    )
    df["rmse_movement_at_peak_velocity"] = df.apply(
        lambda x: _rmse_movement_at_peak_velocity(
            np.concatenate((x["to_target_timestamps"], x["to_center_timestamps"])),
            concatenate_mouse_positions(x),
            x["target_pos"],
            x["to_target_num_timestamps_before_visible"],
        ),
        axis=1,
    )
    return df


def concatenate_mouse_positions(x: np.ndarray) -> np.ndarray:
    """
    concatenate the "to_target_mouse_positions" and "to_center_mouse_positions"

    :param x: the data to concatenate
    :return: the concatenated result
    """
    return np.concatenate(
        (
            x["to_target_mouse_positions"],
            x["to_center_mouse_positions"].reshape(
                x["to_center_mouse_positions"].shape[0], 2
            ),
        )
    )


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
) -> float:
    """
    The reaction time is defined as the timestamp where the cursor first moves,
    minus the timestamp where the target becomes visible.
    This means the reaction time can be negative if the cursor is moved before
    the target is made visible.

    :param mouse_times: The array of timestamps
    :param mouse_positions: The array of mouse positions
    :param to_target_num_timestamps_before_visible: The index of the first timestamp where the target is visible
    :return: The reaction time
    """
    if (
        mouse_times.shape[0] != mouse_positions.shape[0]
        or mouse_times.shape[0] == 0
        or mouse_times.shape[0] < to_target_num_timestamps_before_visible
    ):
        return np.nan
    i = 0
    while xydist(mouse_positions[0], mouse_positions[i]) < min_distance and i + 1 < len(
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
    :return: The RMSE of the distance from the ideal trajectory
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


def _area(
    to_target_mouse_positions: np.ndarray, to_center_mouse_positions: np.ndarray
) -> float:
    """
    Calculates the total area enclosed by the mouse positions and the corresponding list of closed polygons

    Uses the built-in operation `area` in the library `shapely` to calculate the area of geometry object.
    However this is only available for valid (not self intersected) geometries.
    To tackle the self-intersection problem,
    the strategy is to split one self intersected object into the union of LineString (a geometry type composed of one or more line segments),
    then construct a bunch of valid polygons from these lines,
    then calculate the area of each valid polygon and sum them up.

    :param to_target_mouse_positions: x,y mouse positions moving towards the target
    :param to_center_mouse_positions: x,y mouse positions moving towards the center
    :return: area

    """
    coords = get_closed_polygon(to_target_mouse_positions, to_center_mouse_positions)
    polygons = polygonize(unary_union(LineString(coords)))
    area = sum(polygon.area for polygon in polygons)
    return area


def _normalized_area(
    to_target_mouse_positions: np.ndarray, to_center_mouse_positions: np.ndarray
) -> float:
    """
    normalized area = (the area formed by paths) / (length of the paths)²

    :param to_target_mouse_positions: x,y mouse positions moving towards the target
    :param to_center_mouse_positions: x,y mouse positions moving towards the center
    :return: normalized area
    """
    area = _area(to_target_mouse_positions, to_center_mouse_positions)
    movement_length = get_movement_length(
        to_target_mouse_positions, to_center_mouse_positions
    )

    normalized_area = area / (movement_length**2) if movement_length != 0 else 0
    return normalized_area


def get_movement_length(
    to_target_mouse_positions: np.ndarray, to_center_mouse_positions: np.ndarray
) -> float:
    """
    calculate the length of the paths connecting the target and the center
    if only 1 path exists, another path is the distance between the head and tail of the existing path.

    :param to_target_mouse_positions: x,y mouse positions moving towards the target
    :param to_center_mouse_positions: x,y mouse positions moving towards the center
    :return: length of the movement
    """
    closed_polygon_coords = get_closed_polygon(
        to_target_mouse_positions, to_center_mouse_positions
    )
    movement_length = _distance(closed_polygon_coords)
    return movement_length


def get_closed_polygon(
    to_target_mouse_positions: np.ndarray, to_center_mouse_positions: np.ndarray
) -> np.ndarray:
    """
    connect the to target path and to center path to a closed polygon

    :param to_target_mouse_positions: x,y mouse positions moving towards the target
    :param to_center_mouse_positions: x,y mouse positions moving towards the center
    :return: x,y mouse positions of the closed polygon

    """
    to_target_mouse_positions = preprocess_mouse_positions(to_target_mouse_positions)
    to_center_mouse_positions = preprocess_mouse_positions(to_center_mouse_positions)
    if to_target_mouse_positions.size == 0:
        return np.concatenate(
            [
                to_center_mouse_positions,
                to_center_mouse_positions[0:1],
            ]
        )
    if to_center_mouse_positions.size == 0:
        return np.concatenate(
            [
                to_target_mouse_positions,
                to_target_mouse_positions[0:1],
            ]
        )

    coords = np.concatenate(
        [
            to_target_mouse_positions,
            to_center_mouse_positions[0:1],
            to_center_mouse_positions,
            to_target_mouse_positions[0:1],
        ]
    )
    return coords


def preprocess_mouse_positions(mouse_positions: np.ndarray) -> np.ndarray:
    """
    reshape the mouse position to (0, 2) if the mouse position is empty, to prevent error happens in the following
    concatenate() function

    :param mouse_positions: x,y mouse positions during movement
    :return: x,y mouse positions after preprocess
    """
    mouse_positions = (
        mouse_positions.reshape(0, 2) if mouse_positions.size == 0 else mouse_positions
    )
    return mouse_positions


def _peak_velocity(
    mouse_times: np.ndarray, mouse_positions: np.ndarray
) -> tuple[np.floating, np.integer]:
    """
    get peak velocity and the corresponding index

    :param mouse_times: The array of timestamps
    :param mouse_positions: The array of mouse positions
    :return: peak velocity and the corresponding index
    """
    velocity = get_velocity(mouse_times, mouse_positions)
    peak_velocity = np.amax(velocity)
    peak_index = np.argmax(velocity)
    return peak_velocity, peak_index


def _peak_acceleration(mouse_times: np.ndarray, mouse_positions: np.ndarray) -> float:
    """
    get peak acceleration

    :param mouse_times: The array of timestamps
    :param mouse_positions: The array of mouse positions
    :return: peak acceleration
    """
    acceleration = get_acceleration(mouse_times, mouse_positions)
    peak_acceleration = np.amax(acceleration)
    return peak_acceleration


def get_derivative(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """
    get derivative dy/dx

    :param y: the array of y
    :param x: the array of x
    :return: the array of dy/dx
    """
    if x.size <= 1 or y.size <= 1:
        return np.array([0])
    dy_dx = np.diff(y) / np.diff(x)
    return dy_dx


def get_velocity(mouse_times: np.ndarray, mouse_positions: np.ndarray) -> np.ndarray:
    """
    get velocity

    :param mouse_times: The array of timestamps
    :param mouse_positions: The array of mouse positions
    :return: the array of velocity
    """
    first_order_derivative = get_derivative(mouse_positions.transpose(), mouse_times)
    velocity = LA.norm(first_order_derivative, axis=0)
    return velocity


def get_acceleration(
    mouse_times: np.ndarray, mouse_positions: np.ndarray
) -> np.ndarray:
    """
    get acceleration

    :param mouse_times: The array of timestamps
    :param mouse_positions: The array of mouse positions
    :return: the array of acceleration
    """
    first_order_derivative = get_derivative(mouse_positions.transpose(), mouse_times)
    second_order_derivative = get_derivative(first_order_derivative, mouse_times[:-1])
    acceleration = LA.norm(second_order_derivative, axis=0)
    return acceleration


def _spatial_error(
    mouse_position: np.ndarray, target: np.ndarray, target_radius: float
) -> float:
    """
    at timeout linear distance from cursor to target - target radius

    :param mouse_position: The array of mouse positions
    :param target: The position of the target
    :param target_radius: radius of the target
    :return: the distance between the end point of the movement to the center of the target - target radius
    """
    if mouse_position.size < 1:
        return 0
    spatial_error = xydist(mouse_position[-1], target) - target_radius
    return max(spatial_error, 0)


def get_first_movement_index(
    mouse_times: np.ndarray,
    mouse_positions: np.ndarray,
    to_target_num_timestamps_before_visible: int,
) -> int | None:
    """
    get index of the first movement in mouse_times

    :param mouse_times: The array of timestamps
    :param mouse_positions: The array of mouse positions
    :param to_target_num_timestamps_before_visible: The index of the first timestamp where the target is visible
    :return: the first movement index in mouse_times
    """
    if (
        mouse_times.shape[0] != mouse_positions.shape[0]
        or mouse_times.shape[0] == 0
        or mouse_times.shape[0] < to_target_num_timestamps_before_visible
    ):
        return None
    i = 0
    while xydist(mouse_positions[0], mouse_positions[i]) < min_distance and i + 1 < len(
        mouse_times
    ):
        i += 1
    return i


def _movement_time_at_peak_velocity(
    mouse_times: np.ndarray,
    mouse_positions: np.ndarray,
    to_target_num_timestamps_before_visible: int,
) -> float:
    """
    get the time from first movement to the peak velocity

    :param mouse_times: The array of timestamps
    :param mouse_positions: The array of mouse positions
    :param to_target_num_timestamps_before_visible: The index of the first timestamp where the target is visible
    :return: the time from first movement to the peak velocity
    """
    i = get_first_movement_index(
        mouse_times, mouse_positions, to_target_num_timestamps_before_visible
    )
    _, peak_index = _peak_velocity(mouse_times, mouse_positions)
    return (
        mouse_times[peak_index] - mouse_times[i]
        if i is not None and peak_index >= i
        else np.nan
    )


def _total_time_at_peak_velocity(
    mouse_times: np.ndarray,
    mouse_positions: np.ndarray,
    to_target_num_timestamps_before_visible: int,
) -> float:
    """
    get the time from the target becomes visible to the peak velocity

    :param mouse_times: The array of timestamps
    :param mouse_positions: The array of mouse positions
    :param to_target_num_timestamps_before_visible: The index of the first timestamp where the target is visible
    :return: the time from the target becomes visible to the peak velocity
    """
    _, peak_index = _peak_velocity(mouse_times, mouse_positions)
    return (
        mouse_times[peak_index] - mouse_times[to_target_num_timestamps_before_visible]
        if to_target_num_timestamps_before_visible < peak_index
        else np.nan
    )


def _movement_distance_at_peak_velocity(
    mouse_times: np.ndarray,
    mouse_positions: np.ndarray,
    to_target_num_timestamps_before_visible: int,
) -> float:
    """
    get the euclidean point-to-point distance travelled from first movement to the peak velocity

    :param mouse_times: The array of timestamps
    :param mouse_positions: The array of mouse positions
    :param to_target_num_timestamps_before_visible: The index of the first timestamp where the target is visible
    :return: the distance travelled from first movement -> the peak velocity
    """
    i = get_first_movement_index(
        mouse_times, mouse_positions, to_target_num_timestamps_before_visible
    )
    _, peak_index = _peak_velocity(mouse_times, mouse_positions)
    return (
        _distance(mouse_positions[i : peak_index + 1])
        if i is not None and peak_index >= i
        else np.nan
    )


def _rmse_movement_at_peak_velocity(
    mouse_times: np.ndarray,
    mouse_positions: np.ndarray,
    target_position: np.ndarray,
    to_target_num_timestamps_before_visible: int,
) -> float:
    """
    The Root Mean Square Error (RMSE) of the perpendicular distance from the peak velocity mouse point
    to the straight line that intersects the first mouse location and the target.

    See: https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Line_defined_by_two_points.

    :param mouse_times: The array of timestamps
    :param mouse_positions: The array of mouse positions
    :param target_position: The position of the target
    :param to_target_num_timestamps_before_visible: The index of the first timestamp where the target is visible
    :return: The RMSE of the distance from the ideal trajectory
    """
    i = get_first_movement_index(
        mouse_times, mouse_positions, to_target_num_timestamps_before_visible
    )
    if i is not None:
        p1 = mouse_positions[i]
    else:
        return np.nan
    p2 = target_position
    _, peak_index = _peak_velocity(mouse_times, mouse_positions)
    p3 = mouse_positions[peak_index]
    return (
        float(LA.norm(np.cross(p2 - p1, p1 - p3)) / LA.norm(p2 - p1))
        if peak_index >= i
        else np.nan
    )
