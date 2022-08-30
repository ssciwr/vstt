from typing import List
from typing import Tuple

import numpy as np
from psychopy.event import xydist


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
    origin = mouse_positions[0]
    norm = np.power(origin[0] - target[0], 2) + np.power(origin[1] - target[1], 2)
    norm *= len(mouse_positions) - 1
    dx = target[0] - origin[0]
    dy = target[1] - origin[1]
    sum_of_squares = 0
    for p in mouse_positions[1:]:
        sum_of_squares += np.power(dx * (origin[1] - p[1]) - dy * (origin[0] - p[0]), 2)
    return np.sqrt(sum_of_squares / norm)
