from __future__ import annotations

from pytest import approx

import vstt


def test_describe_trial() -> None:
    trial = vstt.trial.default_trial()
    assert vstt.trial.describe_trial(trial) == "1 repeat of 8 clockwise targets"
    trial["weight"] = 3
    trial["num_targets"] = 1
    trial["target_order"] = "fixed"
    assert vstt.trial.describe_trial(trial) == "3 repeats of 1 fixed target"
    trial["weight"] = 2
    trial["num_targets"] = 5
    trial["target_order"] = "random"
    assert vstt.trial.describe_trial(trial) == "2 repeats of 5 random targets"


def test_describe_trials() -> None:
    trials = [vstt.trial.default_trial()]
    trial = vstt.trial.default_trial()
    trial["weight"] = 3
    trial["num_targets"] = 1
    trial["target_order"] = "fixed"
    trials.append(trial)
    assert (
        vstt.trial.describe_trials(trials)
        == "  - 1 repeat of 8 clockwise targets\n  - 3 repeats of 1 fixed target"
    )


def test_default_trial() -> None:
    trial = vstt.trial.default_trial()
    assert len(trial) == len(vstt.trial.trial_labels())
    assert isinstance(trial["target_indices"], str)
    assert len(trial["target_indices"].split(" ")) == trial["num_targets"]


def test_trial_labels() -> None:
    trial = vstt.trial.default_trial()
    labels = vstt.trial.trial_labels()
    assert len(trial) == len(labels)
    assert trial.keys() == labels.keys()


def test_import_trial() -> None:
    default_trial = vstt.trial.default_trial()
    trial_dict = {
        "weight": 2,
        "condition_timeout": 0,
        "num_targets": 6,
        "target_order": "clockwise",
        "target_indices": "0 1 2 3 4 5",
        "add_central_target": True,
        "show_target_labels": False,
        "hide_target_when_reached": True,
        "turn_target_to_green_when_reached": False,
        "target_labels": "0 1 2 3 4 5",
        "fixed_target_intervals": False,
        "target_duration": 3,
        "central_target_duration": 3,
        "pre_target_delay": 0,
        "pre_central_target_delay": 0,
        "pre_first_target_extra_delay": 0,
        "target_distance": 0.3,
        "target_size": 0.03,
        "central_target_size": 0.01,
        "show_inactive_targets": False,
        "ignore_incorrect_targets": True,
        "play_sound": True,
        "use_joystick": True,
        "joystick_max_speed": 0.001,
        "show_cursor": False,
        "cursor_size": 0.0123,
        "show_cursor_path": True,
        "automove_cursor_to_center": True,
        "freeze_cursor_between_targets": True,
        "cursor_rotation_degrees": 45,
        "post_trial_delay": 0.2,
        "post_trial_display_results": True,
        "post_block_delay": 2.0,
        "post_block_display_results": False,
        "show_delay_countdown": False,
        "enter_to_skip_delay": True,
    }
    # start with a dict containing valid values for all keys
    for key in default_trial:
        assert key in trial_dict
    # all valid keys are imported
    trial = vstt.trial.import_and_validate_trial(trial_dict)
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
    trial = vstt.trial.import_and_validate_trial(trial_dict)
    for key in trial:
        if key in missing_keys:
            assert trial[key] == default_trial[key]  # type: ignore
        else:
            assert trial[key] == trial_dict[key]  # type: ignore


def test_validate_trial_durations() -> None:
    trial = vstt.trial.default_trial()
    # positive durations are not modified
    trial["target_duration"] = 1
    trial["central_target_duration"] = 1
    trial["pre_target_delay"] = 0.1
    trial["pre_central_target_delay"] = 0.087
    trial["pre_first_target_extra_delay"] = 0.08123
    trial["post_trial_delay"] = 0.2
    trial["post_block_delay"] = 0.7
    vtrial = vstt.trial.import_and_validate_trial(trial)
    assert vtrial["target_duration"] == 1
    assert vtrial["central_target_duration"] == 1
    assert vtrial["pre_target_delay"] == approx(0.1)
    assert vtrial["pre_central_target_delay"] == approx(0.087)
    assert vtrial["pre_first_target_extra_delay"] == approx(0.08123)
    assert vtrial["post_trial_delay"] == approx(0.2)
    assert vtrial["post_block_delay"] == approx(0.7)
    # negative durations are cast to zero
    trial["target_duration"] = -1
    trial["central_target_duration"] = -0.8
    trial["pre_target_delay"] = -0.1
    trial["pre_central_target_delay"] = -0.087
    trial["pre_first_target_extra_delay"] = -0.08123
    trial["post_trial_delay"] = -0.2
    trial["post_block_delay"] = -0.7
    vtrial = vstt.trial.import_and_validate_trial(trial)
    assert vtrial["target_duration"] == 0
    assert vtrial["central_target_duration"] == 0
    assert vtrial["pre_target_delay"] == 0
    assert vtrial["pre_central_target_delay"] == 0
    assert vtrial["pre_first_target_extra_delay"] == 0
    assert vtrial["post_trial_delay"] == 0
    assert vtrial["post_block_delay"] == 0


def test_validate_trial_target_order() -> None:
    trial = vstt.trial.default_trial()
    assert isinstance(trial["target_indices"], str)
    # clockwise
    trial["target_order"] = "clockwise"
    vtrial = vstt.trial.import_and_validate_trial(trial)
    assert isinstance(vtrial["target_indices"], str)
    assert vtrial["target_indices"] == "0 1 2 3 4 5 6 7"
    # anti-clockwise
    trial["target_order"] = "anti-clockwise"
    vtrial = vstt.trial.import_and_validate_trial(trial)
    assert isinstance(vtrial["target_indices"], str)
    assert vtrial["target_indices"] == "7 6 5 4 3 2 1 0"
    # random
    trial["target_order"] = "random"
    vtrial = vstt.trial.import_and_validate_trial(trial)
    assert isinstance(vtrial["target_indices"], str)
    assert len(set(vtrial["target_indices"].split(" "))) == 8
    # fixed & valid
    trial["target_order"] = "fixed"
    trial["target_indices"] = "0 1 2 3 4 5 6 7"
    vtrial = vstt.trial.import_and_validate_trial(trial)
    assert isinstance(vtrial["target_indices"], str)
    assert vtrial["target_indices"] == "0 1 2 3 4 5 6 7"
    # fixed & invalid - clipped to nearest valid indices
    trial["target_order"] = "fixed"
    trial["target_indices"] = "-2 8 1 5 12 -5"
    vtrial = vstt.trial.import_and_validate_trial(trial)
    assert isinstance(vtrial["target_indices"], str)
    assert vtrial["target_indices"] == "0 7 1 5 7 0"
