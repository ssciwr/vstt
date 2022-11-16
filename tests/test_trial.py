from __future__ import annotations

import motor_task_prototype.trial as mtptrial


def test_describe_trial() -> None:
    trial = mtptrial.default_trial()
    assert mtptrial.describe_trial(trial) == "1 repeat of 8 clockwise targets"
    trial["weight"] = 3
    trial["num_targets"] = 1
    trial["target_order"] = "fixed"
    assert mtptrial.describe_trial(trial) == "3 repeats of 1 fixed target"
    trial["weight"] = 2
    trial["num_targets"] = 5
    trial["target_order"] = "random"
    assert mtptrial.describe_trial(trial) == "2 repeats of 5 random targets"


def test_describe_trials() -> None:
    trials = [mtptrial.default_trial()]
    trial = mtptrial.default_trial()
    trial["weight"] = 3
    trial["num_targets"] = 1
    trial["target_order"] = "fixed"
    trials.append(trial)
    assert (
        mtptrial.describe_trials(trials)
        == "  - 1 repeat of 8 clockwise targets\n  - 3 repeats of 1 fixed target"
    )


def test_default_trial() -> None:
    trial = mtptrial.default_trial()
    assert len(trial) == 20
    assert isinstance(trial["target_indices"], str)
    assert len(trial["target_indices"].split(" ")) == trial["num_targets"]


def test_trial_labels() -> None:
    trial = mtptrial.default_trial()
    labels = mtptrial.trial_labels()
    assert len(trial) == len(labels)
    assert trial.keys() == labels.keys()


def test_import_trial() -> None:
    default_trial = mtptrial.default_trial()
    trial_dict = {
        "weight": 2,
        "num_targets": 6,
        "target_order": "clockwise",
        "target_indices": "0 1 2 3 4 5",
        "target_duration": 3,
        "inter_target_duration": 0,
        "target_distance": 0.3,
        "target_size": 0.03,
        "central_target_size": 0.01,
        "show_inactive_targets": False,
        "play_sound": True,
        "show_cursor": False,
        "cursor_size": 0.0123,
        "show_cursor_path": True,
        "automove_cursor_to_center": True,
        "cursor_rotation_degrees": 45,
        "post_trial_delay": 0.2,
        "post_trial_display_results": True,
        "post_block_delay": 2.0,
        "post_block_display_results": False,
    }
    # all valid keys are imported
    trial = mtptrial.import_trial(trial_dict)
    for key in trial:
        assert trial[key] == trial_dict[key]  # type: ignore
    # if any keys are missing, default values are used instead
    missing_keys = [
        "weight",
        "cursor_rotation_degrees",
        "post_trial_delay",
        "post_block_display_results",
    ]
    for key in missing_keys:
        trial_dict.pop(key)
    # unknown keys are ignored
    trial_dict["unknown_key1"] = "ignore me"
    trial_dict["unknown_key2"] = False
    trial = mtptrial.import_trial(trial_dict)
    for key in trial:
        if key in missing_keys:
            assert trial[key] == default_trial[key]  # type: ignore
        else:
            assert trial[key] == trial_dict[key]  # type: ignore


def test_validate_trial_durations() -> None:
    trial = mtptrial.default_trial()
    # positive durations are not modified
    trial["target_duration"] = 1
    trial["inter_target_duration"] = 0.1
    trial["post_trial_delay"] = 0.2
    trial["post_block_delay"] = 0.7
    vtrial = mtptrial.validate_trial(trial)
    assert vtrial["target_duration"] == 1
    assert vtrial["inter_target_duration"] == 0.1
    assert vtrial["post_trial_delay"] == 0.2
    assert vtrial["post_block_delay"] == 0.7
    # negative durations are cast to zero
    trial["target_duration"] = -1
    trial["inter_target_duration"] = -0.1
    trial["post_trial_delay"] = -0.2
    trial["post_block_delay"] = -0.7
    vtrial = mtptrial.validate_trial(trial)
    assert vtrial["target_duration"] == 0
    assert vtrial["inter_target_duration"] == 0
    assert vtrial["post_trial_delay"] == 0
    assert vtrial["post_block_delay"] == 0


def test_validate_trial_target_order() -> None:
    trial = mtptrial.default_trial()
    assert isinstance(trial["target_indices"], str)
    # clockwise
    trial["target_order"] = "clockwise"
    vtrial = mtptrial.validate_trial(trial)
    assert isinstance(vtrial["target_indices"], str)
    assert vtrial["target_indices"] == "0 1 2 3 4 5 6 7"
    # anti-clockwise
    trial["target_order"] = "anti-clockwise"
    vtrial = mtptrial.validate_trial(trial)
    assert isinstance(vtrial["target_indices"], str)
    assert vtrial["target_indices"] == "7 6 5 4 3 2 1 0"
    # random
    trial["target_order"] = "random"
    vtrial = mtptrial.validate_trial(trial)
    assert isinstance(vtrial["target_indices"], str)
    assert len(set(vtrial["target_indices"].split(" "))) == 8
    # fixed & valid
    trial["target_order"] = "fixed"
    trial["target_indices"] = "0 1 2 3 4 5 6 7"
    vtrial = mtptrial.validate_trial(trial)
    assert isinstance(vtrial["target_indices"], str)
    assert vtrial["target_indices"] == "0 1 2 3 4 5 6 7"
    # fixed & invalid - clipped to nearest valid indices
    trial["target_order"] = "fixed"
    trial["target_indices"] = "-2 8 1 5 12 -5"
    vtrial = mtptrial.validate_trial(trial)
    assert isinstance(vtrial["target_indices"], str)
    assert vtrial["target_indices"] == "0 7 1 5 7 0"
