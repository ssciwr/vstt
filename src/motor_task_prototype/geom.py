from typing import Tuple

import numpy as np

"""
An array of `n_points` equidistantly spaced angles in radians
"""


def equidistant_angles(n_points: int) -> np.ndarray:
    return np.linspace(0, n_points - 1.0, n_points) * (2.0 * np.pi / n_points)


def points_on_circle(
    n_points: int, radius: float, include_centre: bool = False
) -> np.ndarray:
    points = [
        [radius * np.sin(angle), radius * np.cos(angle)]
        for angle in equidistant_angles(n_points)
    ]
    if include_centre:
        points.append([0, 0])
    return np.array(points)


"""
Rotate `point` by an angle `angle_radians` around the point `pivot_point`
"""


def rotate_point(
    point: Tuple[float, float],
    angle_radians: float,
    pivot_point: Tuple[float, float] = (0, 0),
) -> Tuple[float, float]:
    s = np.sin(angle_radians)
    c = np.cos(angle_radians)
    x = point[0] - pivot_point[0]
    y = point[1] - pivot_point[1]
    return pivot_point[0] + c * x - s * y, pivot_point[1] + s * x + c * y


class PointRotator:
    """
    Rotate a point (x,y) by a fixed angle in degrees around the origin
    """

    def __init__(self, angle_degrees: float):
        self.angle_degrees = angle_degrees
        angle_radians = angle_degrees * np.pi / 180.0
        self._s = np.sin(angle_radians)
        self._c = np.cos(angle_radians)

    def __call__(self, point: Tuple[float, float]) -> Tuple[float, float]:
        return (
            self._c * point[0] - self._s * point[1],
            self._s * point[0] + self._c * point[1],
        )
