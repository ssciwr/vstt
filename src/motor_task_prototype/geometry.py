import numpy as np


def equidistant_angles(n_points):
    return np.linspace(0, n_points - 1.0, n_points) * (2.0 * np.pi / n_points)


def points_on_circle(n_points, radius):
    return [
        (radius * np.sin(angle), radius * np.cos(angle))
        for angle in equidistant_angles(n_points)
    ]


def rotate_point(point, angle_radians, pivot_point=(0, 0)):
    s = np.sin(angle_radians)
    c = np.cos(angle_radians)
    x = point[0] - pivot_point[0]
    y = point[1] - pivot_point[1]
    return pivot_point[0] + c * x - s * y, pivot_point[1] + s * x + c * y
