from __future__ import annotations

import gui_test_utils as gtu
import motor_task_prototype.trial as mtptrial
from motor_task_prototype.experiment import MotorTaskExperiment
from motor_task_prototype.trials_widget import TrialsWidget
from psychopy.visual.window import Window
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest


def test_trials_widget_no_results(window: Window) -> None:
    widget = TrialsWidget(parent=None, win=window)
    signal_received = gtu.SignalReceived(widget.experiment_modified)
    experiment = MotorTaskExperiment()
    experiment.trial_list = []
    experiment.has_unsaved_changes = False
    assert not signal_received
    assert experiment.trial_handler_with_results is None
    # set an experiment with no trials
    widget.experiment = experiment
    assert widget.experiment is experiment
    assert len(widget.experiment.trial_list) == 0
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is False
    assert widget._btn_move_up.isEnabled() is False
    assert widget._btn_move_down.isEnabled() is False
    assert widget._btn_remove.isEnabled() is False
    assert widget.experiment.has_unsaved_changes is False
    assert not signal_received
    # set an experiment with a single trial & no results
    experiment.trial_list = [mtptrial.default_trial()]
    assert experiment.trial_handler_with_results is None
    assert experiment.has_unsaved_changes is False
    widget.experiment = experiment
    assert widget.experiment is experiment
    # select first row
    QTest.keyClick(widget._widget_list_trials, Qt.Key_Up)
    assert widget.experiment.trial_list == [mtptrial.default_trial()]
    assert widget._widget_list_trials.count() == 1
    assert widget._widget_list_trials.currentRow() == 0
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is True
    assert widget._btn_move_up.isEnabled() is False
    assert widget._btn_move_down.isEnabled() is False
    assert widget._btn_remove.isEnabled() is True
    assert experiment.trial_handler_with_results is None
    assert experiment.has_unsaved_changes is False
    assert not signal_received
    # set an experiment with three trials & no results
    trials = [
        mtptrial.default_trial(),
        mtptrial.default_trial(),
        mtptrial.default_trial(),
    ]
    trials[0]["weight"] = 0
    trials[1]["weight"] = 1
    trials[2]["weight"] = 2
    experiment.trial_list = trials
    assert experiment.trial_handler_with_results is None
    assert experiment.has_unsaved_changes is False
    assert not signal_received
    widget.experiment = experiment
    assert widget.experiment is experiment
    # select first row
    for _ in range(3):
        QTest.keyClick(widget._widget_list_trials, Qt.Key_Up)
    assert [t["weight"] for t in widget.experiment.trial_list] == [0, 1, 2]
    assert widget._widget_list_trials.count() == 3
    assert widget._widget_list_trials.currentRow() == 0
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is True
    assert widget._btn_move_up.isEnabled() is False
    assert widget._btn_move_down.isEnabled() is True
    assert widget._btn_remove.isEnabled() is True
    assert widget.experiment.has_unsaved_changes is False
    assert not signal_received
    # select middle row
    QTest.keyClick(widget._widget_list_trials, Qt.Key_Down)
    assert [t["weight"] for t in widget.experiment.trial_list] == [0, 1, 2]
    assert widget._widget_list_trials.count() == 3
    assert widget._widget_list_trials.currentRow() == 1
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is True
    assert widget._btn_move_up.isEnabled() is True
    assert widget._btn_move_down.isEnabled() is True
    assert widget._btn_remove.isEnabled() is True
    assert widget.experiment.has_unsaved_changes is False
    assert not signal_received
    # select last row
    QTest.keyClick(widget._widget_list_trials, Qt.Key_Down)
    assert [t["weight"] for t in widget.experiment.trial_list] == [0, 1, 2]
    assert widget._widget_list_trials.count() == 3
    assert widget._widget_list_trials.currentRow() == 2
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is True
    assert widget._btn_move_up.isEnabled() is True
    assert widget._btn_move_down.isEnabled() is False
    assert widget._btn_remove.isEnabled() is True
    assert widget.experiment.has_unsaved_changes is False
    assert not signal_received
    # move trial up
    signal_received.clear()
    QTest.mouseClick(widget._btn_move_up, Qt.MouseButton.LeftButton)
    assert [t["weight"] for t in widget.experiment.trial_list] == [0, 2, 1]
    assert widget._widget_list_trials.count() == 3
    assert widget._widget_list_trials.currentRow() == 1
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is True
    assert widget._btn_move_up.isEnabled() is True
    assert widget._btn_move_down.isEnabled() is True
    assert widget._btn_remove.isEnabled() is True
    assert widget.experiment.has_unsaved_changes is True
    assert signal_received
    # move trial down again
    signal_received.clear()
    QTest.mouseClick(widget._btn_move_down, Qt.MouseButton.LeftButton)
    assert [t["weight"] for t in widget.experiment.trial_list] == [0, 1, 2]
    assert widget._widget_list_trials.count() == 3
    assert widget._widget_list_trials.currentRow() == 2
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is True
    assert widget._btn_move_up.isEnabled() is True
    assert widget._btn_move_down.isEnabled() is False
    assert widget._btn_remove.isEnabled() is True
    assert widget.experiment.has_unsaved_changes is True
    assert signal_received
    # remove last trial
    signal_received.clear()
    QTest.mouseClick(widget._btn_remove, Qt.MouseButton.LeftButton)
    QTest.keyClick(widget._widget_list_trials, Qt.Key_Down)
    assert [t["weight"] for t in widget.experiment.trial_list] == [0, 1]
    assert widget._widget_list_trials.count() == 2
    assert widget._widget_list_trials.currentRow() == 1
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is True
    assert widget._btn_move_up.isEnabled() is True
    assert widget._btn_move_down.isEnabled() is False
    assert widget._btn_remove.isEnabled() is True
    assert widget.experiment.has_unsaved_changes is True
    assert signal_received
    # select first trial
    signal_received.clear()
    QTest.keyClick(widget._widget_list_trials, Qt.Key_Up)
    assert [t["weight"] for t in widget.experiment.trial_list] == [0, 1]
    assert widget._widget_list_trials.count() == 2
    assert widget._widget_list_trials.currentRow() == 0
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is True
    assert widget._btn_move_up.isEnabled() is False
    assert widget._btn_move_down.isEnabled() is True
    assert widget._btn_remove.isEnabled() is True
    assert widget.experiment.has_unsaved_changes is True
    assert not signal_received
    # remove first trial
    signal_received.clear()
    QTest.mouseClick(widget._btn_remove, Qt.MouseButton.LeftButton)
    QTest.keyClick(widget._widget_list_trials, Qt.Key_Down)
    assert [t["weight"] for t in widget.experiment.trial_list] == [1]
    assert widget._widget_list_trials.count() == 1
    assert widget._widget_list_trials.currentRow() == 0
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is True
    assert widget._btn_move_up.isEnabled() is False
    assert widget._btn_move_down.isEnabled() is False
    assert widget._btn_remove.isEnabled() is True
    assert widget.experiment.has_unsaved_changes is True
    assert signal_received
    # remove last trial
    signal_received.clear()
    QTest.mouseClick(widget._btn_remove, Qt.MouseButton.LeftButton)
    QTest.keyClick(widget._widget_list_trials, Qt.Key_Down)
    assert widget.experiment.trial_list == []
    assert widget._widget_list_trials.count() == 0
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is False
    assert widget._btn_move_up.isEnabled() is False
    assert widget._btn_move_down.isEnabled() is False
    assert widget._btn_remove.isEnabled() is False
    assert widget.experiment.has_unsaved_changes is True
    assert signal_received


def test_trials_widget_with_results(
    experiment_with_results: MotorTaskExperiment, window: Window
) -> None:
    widget = TrialsWidget(parent=None, win=window)
    signal_received = gtu.SignalReceived(widget.experiment_modified)
    assert not signal_received
    experiment_with_results.has_unsaved_changes = False
    assert experiment_with_results.trial_handler_with_results is not None
    # set an experiment with results
    widget.experiment = experiment_with_results
    # select first row
    for _ in range(3):
        QTest.keyClick(widget._widget_list_trials, Qt.Key_Up)
    # click no when asked if we want to clear the results
    mwt = gtu.ModalWidgetTimer(["N"])
    mwt.start()
    # click on remove button
    QTest.mouseClick(widget._btn_remove, Qt.MouseButton.LeftButton)
    assert not signal_received
    assert experiment_with_results.has_unsaved_changes is False
    assert experiment_with_results.trial_handler_with_results is not None
    # this time click yes when asked if we want to clear the results
    mwt = gtu.ModalWidgetTimer(["Y"])
    mwt.start()
    # click on remove button
    QTest.mouseClick(widget._btn_remove, Qt.MouseButton.LeftButton)
    assert signal_received
    assert experiment_with_results.has_unsaved_changes is True
    assert experiment_with_results.trial_handler_with_results is None
