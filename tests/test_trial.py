import motor_task_prototype.trial as mtptrial
import numpy as np


def test_default_trial() -> None:
    trial = mtptrial.default_trial()
    assert len(trial) == 13
    assert len(trial["target_indices"].split(" ")) == trial["num_targets"]


def test_validate_trial() -> None:
    trial = mtptrial.default_trial()
    assert isinstance(trial["target_indices"], str)
    # clockwise
    trial["target_order"] = "clockwise"
    vtrial = mtptrial.validate_trial(trial)
    assert isinstance(vtrial["target_indices"], np.ndarray)
    assert vtrial["target_indices"].shape == (8,)
    assert np.allclose(vtrial["target_indices"], [0, 1, 2, 3, 4, 5, 6, 7])
    # anti-clockwise
    trial["target_order"] = "anti-clockwise"
    vtrial = mtptrial.validate_trial(trial)
    assert isinstance(vtrial["target_indices"], np.ndarray)
    assert vtrial["target_indices"].shape == (8,)
    assert np.allclose(vtrial["target_indices"], [7, 6, 5, 4, 3, 2, 1, 0])
    # random
    trial["target_order"] = "random"
    vtrial = mtptrial.validate_trial(trial)
    assert isinstance(vtrial["target_indices"], np.ndarray)
    assert vtrial["target_indices"].shape == (8,)
    assert np.allclose(np.sort(vtrial["target_indices"]), [0, 1, 2, 3, 4, 5, 6, 7])
    # fixed & valid
    trial["target_order"] = "fixed"
    trial["target_indices"] = "0 1 2 3 4 5 6 7"
    vtrial = mtptrial.validate_trial(trial)
    assert isinstance(vtrial["target_indices"], np.ndarray)
    assert vtrial["target_indices"].shape == (8,)
    assert np.allclose(vtrial["target_indices"], [0, 1, 2, 3, 4, 5, 6, 7])
    # fixed & invalid - clipped to nearest valid indices
    trial["target_order"] = "fixed"
    trial["target_indices"] = "-2 8 1 5 12 -5"
    vtrial = mtptrial.validate_trial(trial)
    assert isinstance(vtrial["target_indices"], np.ndarray)
    assert vtrial["target_indices"].shape == (6,)
    assert np.allclose(vtrial["target_indices"], [0, 7, 1, 5, 7, 0])
