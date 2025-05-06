from __future__ import annotations

import math

import pytest
from pytest import approx
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot
from qtpy.QtCore import QLocale
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QCheckBox
from qtpy.QtWidgets import QComboBox
from qtpy.QtWidgets import QDialog
from qtpy.QtWidgets import QDoubleSpinBox
from qtpy.QtWidgets import QLineEdit
from qtpy.QtWidgets import QSpinBox
from qtpy.QtWidgets import QTreeWidget
from qtpy.QtWidgets import QVBoxLayout

import vstt
from vstt.trial import TreeDialog
from vstt.trial import get_trial_from_user
from vstt.vtypes import Trial


@pytest.fixture
def mock_trial() -> Trial:
    return vstt.trial.default_trial()


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


def test_trial_groups() -> None:
    """
    test if the elements in trial_groups() exists in trial_labels()
    """
    trial_labels = vstt.trial.trial_labels()
    trial_groups = vstt.trial.trial_groups()
    all_values = [value for sublist in trial_groups.values() for value in sublist]
    for value in all_values:
        assert value in trial_labels


def test_tree_dialog_initialization(mock_trial: Trial) -> None:
    """
    test if TreeDialog initializes correctly.
    """
    tree_dialog = TreeDialog(mock_trial)
    assert tree_dialog.windowTitle() == "Trial Conditions"
    assert isinstance(tree_dialog.tree_layout, QVBoxLayout)
    assert isinstance(tree_dialog.tree_widget, QTreeWidget)
    assert tree_dialog.tree_widget.isHeaderHidden() is True
    assert tree_dialog.trial == mock_trial
    assert tree_dialog.tree_widget.topLevelItemCount() == 18


def test_tree_dialog_updates_trial(qtbot: QtBot, mock_trial: Trial) -> None:
    """
    test if every kind of widget in TreeDialog can be updated correctly.
    """
    dialog = TreeDialog(mock_trial)
    qtbot.addWidget(dialog)
    checkbox = dialog.tree_widget.itemWidget(
        dialog.tree_widget.topLevelItem(0).child(3), 0
    ).findChild(QCheckBox)
    assert checkbox is not None
    initial_state = checkbox.isChecked()
    qtbot.mouseClick(
        checkbox, Qt.LeftButton
    )  # Simulate user clicking 'add_central_target'
    assert dialog.trial["add_central_target"] != initial_state

    spinbox = dialog.tree_widget.itemWidget(
        dialog.tree_widget.topLevelItem(0).child(0), 0
    ).findChild(QSpinBox)
    assert spinbox is not None
    spinbox.selectAll()
    qtbot.keyPress(spinbox, Qt.Key_Backspace)
    qtbot.keyClicks(spinbox, "10")  # Simulate user updating 'num_targets' to '10'
    assert dialog.trial["num_targets"] == 10

    double_spinbox = dialog.tree_widget.itemWidget(
        dialog.tree_widget.topLevelItem(0).child(15), 0
    ).findChild(QDoubleSpinBox)
    double_spinbox.setLocale(
        QLocale(QLocale.English)
    )  # Explicitly set the double_spinbox’s locale
    assert double_spinbox is not None
    double_spinbox.selectAll()
    qtbot.keyPress(double_spinbox, Qt.Key_Backspace)
    qtbot.keyClicks(
        double_spinbox, "0.08"
    )  # Simulate user updating 'target_size' to '0.08'
    assert math.isclose(dialog.trial["target_size"], 0.08) is True

    combobox = dialog.tree_widget.itemWidget(
        dialog.tree_widget.topLevelItem(0).child(1), 0
    ).findChild(QComboBox)
    assert combobox is not None
    qtbot.keyClicks(
        combobox, "fixed"
    )  # Simulate user updating 'target_order' to 'fixed'
    assert combobox.currentText() in ["clockwise", "anti-clockwise", "random", "fixed"]
    assert dialog.trial["target_order"] == "fixed"

    line_edit = dialog.tree_widget.itemWidget(
        dialog.tree_widget.topLevelItem(0).child(7), 0
    ).findChild(QLineEdit)
    assert line_edit is not None
    line_edit.selectAll()
    qtbot.keyPress(line_edit, Qt.Key_Backspace)
    qtbot.keyClicks(
        line_edit, "0 1 2 3"
    )  # Simulate user updating 'target_labels' to '0 1 2 3'
    assert dialog.trial["target_labels"] == "0 1 2 3"


def test_tree_dialog_accept(qtbot: QtBot, mock_trial: Trial) -> None:
    """
    test if clicking OK closes the dialog and accepts the input.
    """
    dialog = TreeDialog(mock_trial)
    qtbot.addWidget(dialog)
    qtbot.mouseClick(dialog.ok_button, Qt.LeftButton)
    assert dialog.result() == QDialog.Accepted


def test_get_trial_from_user_accepted(mocker: MockerFixture, mock_trial: Trial) -> None:
    """
    test get_trial_from_user() when dialog is accepted.
    """
    mock_dialog = mocker.patch("vstt.trial.TreeDialog")
    mock_dialog.return_value.exec.return_value = QDialog.Accepted
    mock_dialog.return_value.get_values.return_value = mock_trial
    mock_validate = mocker.patch(
        "vstt.trial.import_and_validate_trial", return_value=mock_trial
    )
    trial_result = get_trial_from_user(mock_trial)
    assert trial_result == mock_trial
    mock_validate.assert_called_once_with(mock_trial)


def test_get_trial_from_user_cancelled(
    mocker: MockerFixture, mock_trial: Trial
) -> None:
    """
    test get_trial_from_user() when dialog is cancelled.
    """
    mock_dialog = mocker.patch("vstt.trial.TreeDialog")
    mock_dialog.return_value.exec_.return_value = QDialog.Rejected
    trial_result = get_trial_from_user(mock_trial)
    assert trial_result is None
