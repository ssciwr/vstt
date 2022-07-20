import motor_task_prototype.analysis as analysis
import numpy as np


def test_distance() -> None:
    assert np.allclose(analysis.distance([(0, 0)]), [0])
    assert np.allclose(analysis.distance([(0, 0), (1, 1)]), [np.sqrt(2)])
    assert np.allclose(analysis.distance([(0, 0), (1, 1), (0, 0)]), [2.0 * np.sqrt(2)])
    assert np.allclose(
        analysis.distance([(0, 0), (1, 1), (0, 0), (-1, -1)]), [3.0 * np.sqrt(2)]
    )
    assert np.allclose(
        analysis.distance([(0, 0), (1, 1), (0, 0), (-1, -1), (1, 1)]),
        [5.0 * np.sqrt(2)],
    )
    assert np.allclose(
        analysis.distance([(0, 0), (np.sqrt(2), np.sqrt(2)), (0, 0)]), [4]
    )


def test_reaction_movement_times() -> None:
    for times in [
        [0.0],
        [0.0, 0.1],
        [1.0, 2.0],
        [0.0, 2.0, 4.0, 6.0],
        [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.1, 1.2],
    ]:
        n = len(times)
        for n_zeros in range(n):
            positions = [(-1e-13, 1e-14)] * n_zeros + [(1, 1)] * (n - n_zeros)
            reaction_time = times[n_zeros] - times[0]
            movement_time = times[-1] - reaction_time
            assert np.allclose(
                analysis.reaction_movement_times(times, positions),
                [reaction_time, movement_time],
            )


def test_rmse() -> None:
    target = (1, 1)
    origin = (0, 0)
    # all points lie on line
    assert np.allclose(analysis.rmse([(0, 0)], target, origin), [0])
    assert np.allclose(analysis.rmse([(0, 0), (1, 1)], target, origin), [0])
    assert np.allclose(analysis.rmse([(0, 0), (0.2, 0.2)], target, origin), [0])
    assert np.allclose(
        analysis.rmse([(0, 0), (0.25, 0.25), (0.5, 0.5), (0.75, 0.75)], target, origin),
        [0],
    )
    # points which are all 1/sqrt(2) perpendicular distance from line
    assert np.allclose(analysis.rmse([(0, 1)], target, origin), [1.0 / np.sqrt(2.0)])
    assert np.allclose(analysis.rmse([(1, 0)], target, origin), [1.0 / np.sqrt(2.0)])
    assert np.allclose(
        analysis.rmse([(0, 1), (1, 0)], target, origin), [1.0 / np.sqrt(2.0)]
    )
    assert np.allclose(
        analysis.rmse([(0, 1), (1, 0), (0, 1), (1, 0)], target, origin),
        [1.0 / np.sqrt(2.0)],
    )
