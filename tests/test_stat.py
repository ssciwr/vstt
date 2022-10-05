from __future__ import annotations

import motor_task_prototype.stat as mptstat
import numpy as np


def test_distance() -> None:
    assert np.allclose(mptstat.distance([(0, 0)]), [0])
    assert np.allclose(mptstat.distance([(3, 4)]), [0])
    assert np.allclose(mptstat.distance([(0, 0), (1, 1)]), [np.sqrt(2)])
    assert np.allclose(mptstat.distance([(1, 1), (0, 0)]), [np.sqrt(2)])
    assert np.allclose(mptstat.distance([(0, 0), (1, 1), (0, 0)]), [2.0 * np.sqrt(2)])
    assert np.allclose(
        mptstat.distance([(0, 0), (1, 1), (0, 0), (-1, -1)]), [3.0 * np.sqrt(2)]
    )
    assert np.allclose(
        mptstat.distance([(0, 0), (1, 1), (0, 0), (-1, -1), (1, 1)]),
        [5.0 * np.sqrt(2)],
    )
    assert np.allclose(
        mptstat.distance([(0, 0), (np.sqrt(2), np.sqrt(2)), (0, 0)]), [4]
    )


def test_reaction_movement_times() -> None:
    for times in [
        [0.0, 0.1],
        [1.0, 2.0],
        [0.0, 2.0, 4.0, 6.0],
        [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.1, 1.2],
    ]:
        n = len(times)
        for n_zeros in range(1, n):
            positions = [(-1e-13, 1e-14)] * n_zeros + [(1, 1)] * (n - n_zeros)
            reaction_time = max(0.0, times[n_zeros] - times[1])
            movement_time = times[-1] - times[n_zeros]
            assert np.allclose(
                mptstat.reaction_movement_times(times, positions),
                [reaction_time, movement_time],
            )


def test_rmse() -> None:
    target = (1, 1)
    # all points lie on line
    assert np.allclose(mptstat.rmse([(0, 0), (1, 1)], target), [0])
    assert np.allclose(mptstat.rmse([(0, 0), (0.2, 0.2)], target), [0])
    assert np.allclose(
        mptstat.rmse([(0, 0), (0.25, 0.25), (0.5, 0.5), (0.75, 0.75)], target),
        [0],
    )
    # points which are all 1/sqrt(2) perpendicular distance from line
    assert np.allclose(mptstat.rmse([(0, 0), (0, 1)], target), [1.0 / np.sqrt(2.0)])
    assert np.allclose(mptstat.rmse([(0, 0), (1, 0)], target), [1.0 / np.sqrt(2.0)])
    assert np.allclose(
        mptstat.rmse([(0, 0), (0, 1), (1, 0)], target), [1.0 / np.sqrt(2.0)]
    )
    assert np.allclose(
        mptstat.rmse([(0, 0), (0, 1), (1, 0), (0, 1), (1, 0)], target),
        [1.0 / np.sqrt(2.0)],
    )
