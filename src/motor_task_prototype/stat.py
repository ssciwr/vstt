from __future__ import annotations

from typing import List
from typing import Tuple

import numpy as np
from psychopy.data import TrialHandlerExt
from psychopy.event import xydist


class MotorTaskStats:
    def __init__(self, trial_handler: TrialHandlerExt, trials: List[int]):
        all_to_target_reaction_times: List[List[float]] = []
        all_to_target_times: List[List[float]] = []
        all_to_target_distances: List[List[float]] = []
        all_to_target_rmses: List[List[float]] = []
        all_to_center_reaction_times: List[List[float]] = []
        all_to_center_times: List[List[float]] = []
        all_to_center_distances: List[List[float]] = []
        all_to_center_rmses: List[List[float]] = []
        if trial_handler is None:
            return
        data = trial_handler.data
        # for now assume the experiment is only repeated once
        i_repeat = 0
        for i_trial in trials:
            targets = data["target_pos"][i_trial][i_repeat]
            n_targets = len(targets)
            to_target_reaction_times = [0.0] * n_targets
            to_target_times = [0.0] * n_targets
            to_target_distances = [0.0] * n_targets
            to_target_rmses = [0.0] * n_targets
            for (
                to_target_timestamps,
                to_target_mouse_positions,
                target_pos,
                target_index,
            ) in zip(
                data["to_target_timestamps"][i_trial][i_repeat],
                data["to_target_mouse_positions"][i_trial][i_repeat],
                targets,
                data["target_indices"][i_trial][i_repeat],
            ):
                to_target_reaction_time, to_target_time = reaction_movement_times(
                    to_target_timestamps, to_target_mouse_positions
                )
                to_target_reaction_times[target_index] = to_target_reaction_time
                to_target_times[target_index] = to_target_time
                to_target_distances[target_index] = distance(to_target_mouse_positions)
                to_target_rmses[target_index] = rmse(
                    to_target_mouse_positions, target_pos
                )
            all_to_target_reaction_times.append(to_target_reaction_times)
            all_to_target_times.append(to_target_times)
            all_to_target_distances.append(to_target_distances)
            all_to_target_rmses.append(to_target_rmses)
            to_center_reaction_times = [0.0] * n_targets
            to_center_times = [0.0] * n_targets
            to_center_distances = [0.0] * n_targets
            to_center_rmses = [0.0] * n_targets
            central_target = (0.0, 0.0)
            for to_center_timestamps, to_center_mouse_positions, target_index in zip(
                data["to_center_timestamps"][i_trial][i_repeat],
                data["to_center_mouse_positions"][i_trial][i_repeat],
                data["target_indices"][i_trial][i_repeat],
            ):
                to_center_reaction_time, to_center_time = reaction_movement_times(
                    to_center_timestamps, to_center_mouse_positions
                )
                to_center_reaction_times[target_index] = to_center_reaction_time
                to_center_times[target_index] = to_center_time
                to_center_distances[target_index] = distance(to_center_mouse_positions)
                to_center_rmses[target_index] = rmse(
                    to_center_mouse_positions, central_target
                )
            all_to_center_reaction_times.append(to_center_reaction_times)
            all_to_center_times.append(to_center_times)
            all_to_center_distances.append(to_center_distances)
            all_to_center_rmses.append(to_center_rmses)
        self.to_target_reaction_times: np.ndarray = np.array(
            all_to_target_reaction_times
        )
        self.to_target_times: np.ndarray = np.array(all_to_target_times)
        self.to_target_distances: np.ndarray = np.array(all_to_target_distances)
        self.to_target_rmses: np.ndarray = np.array(all_to_target_rmses)
        self.to_center_reaction_times: np.ndarray = np.array(
            all_to_center_reaction_times
        )
        self.to_center_times: np.ndarray = np.array(all_to_center_times)
        self.to_center_distances: np.ndarray = np.array(all_to_center_distances)
        self.to_center_rmses: np.ndarray = np.array(all_to_center_rmses)


def reaction_movement_times(
    mouse_times: List[float],
    mouse_positions: List[Tuple[float, float]],
    epsilon: float = 1e-12,
) -> Tuple[float, float]:
    assert len(mouse_times) == len(
        mouse_positions
    ), "Mouse times and positions lists must have the same number of elements"
    assert len(mouse_times) > 1
    i = 1
    while xydist(mouse_positions[0], mouse_positions[i]) < epsilon and i + 1 < len(
        mouse_times
    ):
        i += 1
    reaction_time = mouse_times[i] - mouse_times[1]
    movement_time = mouse_times[-1] - mouse_times[i]
    return reaction_time, movement_time


def distance(mouse_positions: List[Tuple[float, float]]) -> float:
    dist = 0
    for i in range(len(mouse_positions) - 1):
        dist += xydist(mouse_positions[i + 1], mouse_positions[i])
    return dist


def rmse(
    mouse_positions: List[Tuple[float, float]], target: Tuple[float, float]
) -> float:
    assert len(mouse_positions) > 1
    # use first mouse position as origin point, so exclude it from RMSE measure
    x1, y1 = mouse_positions[0]
    x2, y2 = target
    norm = np.power(x2 - x1, 2) + np.power(y2 - y1, 2)
    norm *= len(mouse_positions) - 1
    sum_of_squares = 0
    for x0, y0 in mouse_positions[1:]:
        sum_of_squares += np.power((x2 - x1) * (y1 - y0) - (x1 - x0) * (y2 - y1), 2)
    return np.sqrt(sum_of_squares / norm)
