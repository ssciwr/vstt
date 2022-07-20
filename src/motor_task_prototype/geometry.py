import numpy as np
from typing import List, Tuple


def equidistant_angles(n_points: int) -> np.ndarray:
    return np.linspace(0, n_points - 1.0, n_points) * (2.0 * np.pi / n_points)


def points_on_circle(n_points: int, radius: float) -> List[Tuple[float, float]]:
    return [
        (radius * np.sin(angle), radius * np.cos(angle))
        for angle in equidistant_angles(n_points)
    ]


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


class RotatedPoint:
    """
    Rotate a point (x,y) by a fixed angle around the origin
    """

    def __init__(self, angle_radians: float):
        self.angle = angle_radians
        self._s = np.sin(angle_radians)
        self._c = np.cos(angle_radians)

    def __call__(self, point: Tuple[float, float]) -> Tuple[float, float]:
        return (
            self._c * point[0] - self._s * point[1],
            self._s * point[0] + self._c * point[1],
        )
