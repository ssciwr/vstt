from __future__ import annotations

import numpy as np


def equidistant_angles(n_points: int) -> np.ndarray:
    """
    An array of `n_points` equidistantly spaced angles in radians
    """
    max_angle = 2.0 * np.pi * (n_points - 1.0) / n_points
    return np.linspace(0, max_angle, n_points)


def points_on_circle(
    n_points: int, radius: float, include_centre: bool = False
) -> np.ndarray:
    points = [
        [radius * np.sin(angle), radius * np.cos(angle)]
        for angle in equidistant_angles(n_points)
    ]
    if include_centre:
        points.append([0.0, 0.0])
    return np.array(points)


def rotate_point(
    point: tuple[float, float],
    angle_radians: float,
    pivot_point: tuple[float, float] = (0, 0),
) -> tuple[float, float]:
    """
    Rotate `point` by an angle `angle_radians` around the point `pivot_point`
    """
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

    def __call__(self, point: tuple[float, float]) -> np.ndarray:
        return np.array(
            [
                self._c * point[0] - self._s * point[1],
                self._s * point[0] + self._c * point[1],
            ]
        )


class JoystickPointUpdater:
    """
    Update a point (x,y) according to a velocity vector (vx, vy), with optional rotation of the vector

    vx, vy should lie in the range [-1, 1]

    The returned point is given by

    x -> x + `max_speed` * vx'
    y -> y + `max_speed` * vy'

    Where (vx',vy') is (vx, vy) rotated by `angle_degrees`

    The returned point is clipped to lie within the screen,
    where the screen has height 1 and (0,0) lies in the centre of the screen
    So the y-range is always [-0.5, 0.5], and the x-range is this multiplied by (width/height)
    """

    def __init__(
        self,
        angle_degrees: float,
        max_speed: float,
        window_size: np.ndarray | None = None,
    ):
        self.angle_degrees = angle_degrees
        self.max_speed = max_speed
        if window_size is not None and window_size.shape[-1] >= 2:
            self.clip_window = 0.5 * np.array([window_size[0] / window_size[1], 1.0])
        else:
            self.clip_window = np.array([0.5, 0.5])
        angle_radians = angle_degrees * np.pi / 180.0
        self._s = self.max_speed * np.sin(angle_radians)
        self._c = self.max_speed * np.cos(angle_radians)

    def __call__(self, point: np.ndarray, velocity: tuple[float, float]) -> np.ndarray:
        return np.clip(
            np.array(
                [
                    point[0] + self._c * velocity[0] + self._s * velocity[1],
                    point[1] + self._s * velocity[0] - self._c * velocity[1],
                ]
            ),
            -self.clip_window,
            self.clip_window,
        )


def to_target_dists(
    pos: np.ndarray, target_xys: np.ndarray, target_index: int, has_central_target: bool
) -> tuple[float, float]:
    rms_dists = np.linalg.norm(target_xys - np.array(pos), axis=1)
    n_targets_excluding_central = target_xys.shape[0]
    if has_central_target:
        # exclude central target from "distance to any target" measure
        n_targets_excluding_central = n_targets_excluding_central - 1
    # dist to correct target, min distance to any target (excluding center target)
    return rms_dists[target_index], np.min(rms_dists[:n_targets_excluding_central])
