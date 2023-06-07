from __future__ import annotations

import numpy as np
import vstt
from vstt.experiment import Experiment


def test_data_df(experiment_with_results: Experiment) -> None:
    # results from 3 reps of 8-target trial, 1 rep of 4-target trial with automove back to center
    df = vstt.stats._data_df(experiment_with_results.trial_handler_with_results)
    assert len(df.columns) == len(vstt.stats._get_trial_data_columns())
    for index, row in df.iterrows():
        assert row["to_target_mouse_positions"].shape[1] == 2
        assert (
            row["to_center_mouse_positions"].shape[0] == 0
            or row["to_center_mouse_positions"].shape[1] == 2
        )
        assert (
            row["to_target_timestamps"].shape[0]
            == row["to_target_mouse_positions"].shape[0]
        )
        assert (
            row["to_center_timestamps"].shape[0]
            == row["to_center_mouse_positions"].shape[0]
        )
    weights = [3, 1]
    targets = [8, 4]
    rows, cols = df.shape
    assert rows == np.sum(np.multiply(weights, targets))
    assert np.allclose(df["i_trial"].unique(), list(range(np.sum(weights))))
    assert df["i_rep"].unique() == [0]
    for i in [0, 1]:
        assert np.allclose(
            df.loc[df.condition_index == i]["i_target"].unique(),
            list(range(targets[i])),
        )


def test_stats_df(experiment_with_results: Experiment) -> None:
    df = vstt.stats.stats_dataframe(experiment_with_results.trial_handler_with_results)
    assert np.alltrue(np.isnan(df.loc[df.condition_index == 1]["to_center_time"]))
    for destination, stat_label_units in vstt.stats.list_dest_stat_label_units():
        for stat, label, unit in stat_label_units:
            assert stat in df.columns


def test_distance() -> None:
    assert np.allclose(vstt.stats._distance(np.array([[0, 0]])), [0])
    assert np.allclose(vstt.stats._distance(np.array([[3, 4]])), [0])
    assert np.allclose(vstt.stats._distance(np.array([[0, 0], [1, 1]])), [np.sqrt(2)])
    assert np.allclose(vstt.stats._distance(np.array([[1, 1], [0, 0]])), [np.sqrt(2)])
    assert np.allclose(
        vstt.stats._distance(np.array([[0, 0], [1, 1], [0, 0]])), [2.0 * np.sqrt(2)]
    )
    assert np.allclose(
        vstt.stats._distance(np.array([[0, 0], [1, 1], [0, 0], [-1, -1]])),
        [3.0 * np.sqrt(2)],
    )
    assert np.allclose(
        vstt.stats._distance(np.array([[0, 0], [1, 1], [0, 0], [-1, -1], [1, 1]])),
        [5.0 * np.sqrt(2)],
    )
    assert np.allclose(
        vstt.stats._distance(np.array([[0, 0], [np.sqrt(2), np.sqrt(2)], [0, 0]])), [4]
    )


def test_reaction_movement_time() -> None:
    for times in [
        [0.0, 0.1],
        [-1.0, -0.5],
        [0.0, 2.0, 4.0, 6.0],
        [-0.9, -0.7, -0.5, -0.3, -0.1, 0.1, 0.3, 0.5],
        [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.1, 1.2],
    ]:
        n = len(times)
        for n_zeros in range(1, n):
            for n_before_visible in range(1, n):
                positions = [[-1e-13, 1e-14]] * n_zeros + [[1, 1]] * (n - n_zeros)
                reaction_time = times[n_zeros] - times[n_before_visible]
                assert np.allclose(
                    vstt.stats._reaction_time(
                        np.array(times), np.array(positions), n_before_visible
                    ),
                    [reaction_time],
                )


def test_rmse() -> None:
    target = np.array([1, 1])
    # all points lie on the straight line between start and end point
    assert np.allclose(vstt.stats._rmse(np.array([(0, 0), (1, 1)]), target), [0])
    assert np.allclose(vstt.stats._rmse(np.array([(0, 0), (0.2, 0.2)]), target), [0])
    assert np.allclose(
        vstt.stats._rmse(
            np.array([(0, 0), (0.25, 0.25), (0.5, 0.5), (0.75, 0.75)]), target
        ),
        [0],
    )
    # points which are all 1/sqrt(2) perpendicular distance from line
    assert np.allclose(
        vstt.stats._rmse(np.array([(0, 0), (0, 1)]), target), [1.0 / np.sqrt(2.0)]
    )
    assert np.allclose(
        vstt.stats._rmse(np.array([(0, 0), (1, 0)]), target), [1.0 / np.sqrt(2.0)]
    )
    assert np.allclose(
        vstt.stats._rmse(np.array([(0, 0), (0, 1), (1, 0)]), target),
        [1.0 / np.sqrt(2.0)],
    )
    assert np.allclose(
        vstt.stats._rmse(np.array([(0, 0), (0, 1), (1, 0), (0, 1), (1, 0)]), target),
        [1.0 / np.sqrt(2.0)],
    )
