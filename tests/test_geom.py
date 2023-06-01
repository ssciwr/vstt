from __future__ import annotations

import numpy as np
import vstt


def test_equidistant_angles() -> None:
    assert np.allclose(vstt.geom.equidistant_angles(1) / np.pi, [0])
    assert np.allclose(vstt.geom.equidistant_angles(2) / np.pi, [0, 1])
    assert np.allclose(
        vstt.geom.equidistant_angles(3) / np.pi, [0, 2.0 / 3.0, 4.0 / 3.0]
    )
    assert np.allclose(vstt.geom.equidistant_angles(4) / np.pi, [0, 0.5, 1.0, 1.5])


def test_points_on_circle() -> None:
    assert np.allclose(vstt.geom.points_on_circle(1, 0.2), [(0.0, 0.2)])
    assert np.allclose(
        vstt.geom.points_on_circle(1, 0.2, include_centre=True),
        [(0.0, 0.2), (0.0, 0.0)],
    )
    assert np.allclose(vstt.geom.points_on_circle(2, 0.5), [(0.0, 0.5), (0.0, -0.5)])
    assert np.allclose(
        vstt.geom.points_on_circle(4, 1.0), [(0, 1), (1, 0), (0, -1), (-1, 0)]
    )


def test_rotate_point() -> None:
    pivots = [(0, 0), (0.3, 0.2), (-0.3, 0.4), (0.6, -0.4), (-1, -1)]
    points = [(1, 0.2), (-1, 0.2), (-0.7, -0.5), (0.7, 0.0), (0.0, 0.6), (0, 0)]
    angles = [0, -0.1, 0.3, 0.66, np.pi, -np.pi, 4.5, -5.2, 2.0 * np.pi]
    # rotate by zero or 360 degrees around any pivot point returns original point
    for angle in [0, -2 * np.pi, 2 * np.pi]:
        for pivot in pivots:
            for point in points:
                assert np.allclose(vstt.geom.rotate_point(point, angle, pivot), point)
    # rotating a point around itself returns the original point
    for angle in angles:
        for point in points:
            assert np.allclose(vstt.geom.rotate_point(point, angle, point), point)
    # rotating by +n degrees is equivalent to rotating by n-360 degrees
    for angle in angles:
        equivalent_angle = angle - 2 * np.pi
        for pivot in pivots:
            for point in points:
                assert np.allclose(
                    vstt.geom.rotate_point(point, angle, pivot),
                    vstt.geom.rotate_point(point, equivalent_angle, pivot),
                )


def test_point_rotator() -> None:
    for angle_radians in [0, -0.1, 0.3, 0.66, np.pi, -np.pi, 4.5]:
        angle_degrees = 180.0 * angle_radians / np.pi
        rp = vstt.geom.PointRotator(angle_degrees)
        for point in [
            (1, 0.2),
            (-1, 0.2),
            (-0.7, -0.5),
            (0.7, 0.0),
            (0.0, 0.6),
            (0, 0),
        ]:
            p1 = rp(point)
            p2 = vstt.geom.rotate_point(point, angle_radians, (0, 0))
            assert np.allclose([p1], [p2])


def test_joystick_point_updater_clipped() -> None:
    for window_size in [
        None,
        np.array([1]),
        np.array([800, 600]),
        np.array([2000, 3000]),
    ]:
        max_h = 0.5
        if window_size is not None and window_size.shape[-1] > 1:
            max_w = 0.5 * window_size[0] / window_size[1]
        else:
            max_w = 0.5
        jpu = vstt.geom.JoystickPointUpdater(
            angle_degrees=0, max_speed=0.123, window_size=window_size
        )
        for x0 in [np.array([0, 0]), np.array([0.4, -0.7]), np.array([12, 18])]:
            # default clipping if no window_size provided is to [-0.5, 0.5]
            # (note: + value joystick in y direction points down!)
            assert np.allclose(jpu(x0, (215423, 23423423)), [max_w, -max_h])
            assert np.allclose(jpu(x0, (215423, -23423423)), [max_w, max_h])
            assert np.allclose(jpu(x0, (-215423, 23423423)), [-max_w, -max_h])
            assert np.allclose(jpu(x0, (-215423, -23423423)), [-max_w, max_h])


def test_joystick_point_updater_no_clipping() -> None:
    # low max speed to avoid clipping returned values
    max_speed = 0.0001345112
    window_size = np.array([800, 600])
    for angle_radians in [0, -0.1, 0.3, 0.66, np.pi, -np.pi, 4.5]:
        angle_degrees = 180.0 * angle_radians / np.pi
        jpu = vstt.geom.JoystickPointUpdater(
            angle_degrees=angle_degrees, max_speed=max_speed, window_size=window_size
        )
        # small initial points to avoid clipping returned values
        for p0 in [
            np.array([0, 0]),
            np.array([0.002355, 0.0065334]),
            np.array([-0.00567565, 0.005464534]),
            np.array([-0.0046543235, -0.00124346344]),
        ]:
            for v in [
                (1, 0.2),
                (-1, 0.2),
                (-0.7, -0.5),
                (0.7, 0.0),
                (0.0, 0.6),
                (0, 0),
            ]:
                # invert y direction of vector to simulate joystick input (+y points down)
                p1 = jpu(p0, (v[0], -v[1]))
                # rotate vector, rescale, add to point
                p2 = p0 + max_speed * np.array(
                    vstt.geom.rotate_point((v[0], v[1]), angle_radians, (0, 0))
                )
                assert np.allclose(p1, p2)


def test_to_target_dists() -> None:
    p = np.array([0.0, 0.0])
    xys = np.array([[1.0, 0], [0.0, 0.0]])
    dist_correct, dist_any = vstt.geom.to_target_dists(
        p, xys, 0, has_central_target=True
    )
    assert dist_correct == 1.0
    assert dist_any == 1.0
    dist_correct, dist_any = vstt.geom.to_target_dists(
        p, xys, 0, has_central_target=False
    )
    assert dist_correct == 1.0
    assert dist_any == 0.0
    #
    p = np.array([1.0, 0.0])
    xys = np.array([[1.0, 1.0], [1.0, 0.0], [-1.0, 0.0], [0.0, 0.0]])
    for has_central_target in [True, False]:
        dist_correct, dist_any = vstt.geom.to_target_dists(
            p, xys, 0, has_central_target
        )
        assert dist_correct == 1.0
        assert dist_any == 0.0
        dist_correct, dist_any = vstt.geom.to_target_dists(
            p, xys, 1, has_central_target
        )
        assert dist_correct == 0.0
        assert dist_any == 0.0
        dist_correct, dist_any = vstt.geom.to_target_dists(
            p, xys, 2, has_central_target
        )
        assert dist_correct == 2.0
        assert dist_any == 0.0
        dist_correct, dist_any = vstt.geom.to_target_dists(
            p, xys, 3, has_central_target
        )
        assert dist_correct == 1.0
        assert dist_any == 0.0
