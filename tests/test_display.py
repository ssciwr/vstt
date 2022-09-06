import motor_task_prototype.display as mtpdisplay
import pytest


def test_display_options_labels() -> None:
    display_options = mtpdisplay.default_display_options()
    labels = mtpdisplay.display_options_labels()
    assert len(display_options) == len(labels)
    assert display_options.keys() == labels.keys()


def test_import_display_options(caplog: pytest.LogCaptureFixture) -> None:
    default_display_options = mtpdisplay.default_display_options()
    display_options_dict = {
        "to_target_paths": True,
        "to_center_paths": "I should be a bool!",
        "targets": True,
        "central_target": True,
        "to_target_reaction_time": True,
        "to_center_reaction_time": True,
        "to_target_time": True,
        "to_center_time": True,
        "to_target_distance": False,
        "to_center_distance": False,
        "to_target_rmse": False,
        "to_center_rmse": False,
        "averages": True,
        "unknown_key1": "ignore me",
        "unknown_key2": False,
    }
    # if any keys are missing or have invalid values, default values are used instead
    missing_keys = [
        "to_center_reaction_time",
        "to_target_rmse",
        "to_center_rmse",
    ]
    for key in missing_keys:
        display_options_dict.pop(key)
    invalid_values = ["to_center_paths"]
    display_options = mtpdisplay.import_display_options(display_options_dict)
    for key in display_options:
        if key in missing_keys or key in invalid_values:
            assert display_options[key] == default_display_options[key]  # type: ignore
        else:
            assert display_options[key] == display_options_dict[key]  # type: ignore
    log_messages = {r.message for r in caplog.records}
    expected_log_messages = {
        "Key 'to_center_reaction_time' missing, using default 'False'",
        "Key 'to_target_rmse' missing, using default 'True'",
        "Key 'to_center_rmse' missing, using default 'False'",
        "Key 'to_center_paths' invalid: expected <class 'bool'>, got <class 'str'> 'I should be a bool!'",
        "Ignoring unknown key 'unknown_key1'",
        "Ignoring unknown key 'unknown_key2'",
    }
    assert log_messages == expected_log_messages
