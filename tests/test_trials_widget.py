import motor_task_prototype.trial as mtptrial
from motor_task_prototype.trials_widget import TrialsWidget
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest


def test_trials_widget() -> None:
    widget = TrialsWidget(None)
    # initially empty
    assert len(widget.get_trial_list()) == 0
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is False
    assert widget._btn_move_up.isEnabled() is False
    assert widget._btn_move_down.isEnabled() is False
    assert widget._btn_remove.isEnabled() is False
    # set a single trial & don't ask for confirmation from user before modification
    trials = [mtptrial.default_trial()]
    widget.set_trial_list(trials, confirm_trial_change_with_user=False)
    # select first row
    QTest.keyClick(widget._widget_list_trials, Qt.Key_Up)
    assert widget.get_trial_list() == trials
    assert widget._widget_list_trials.count() == 1
    assert widget._widget_list_trials.currentRow() == 0
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is True
    assert widget._btn_move_up.isEnabled() is False
    assert widget._btn_move_down.isEnabled() is False
    assert widget._btn_remove.isEnabled() is True
    # set three trials & don't ask for confirmation from user before modification
    trials = [
        mtptrial.default_trial(),
        mtptrial.default_trial(),
        mtptrial.default_trial(),
    ]
    trials[0]["weight"] = 0
    trials[1]["weight"] = 1
    trials[2]["weight"] = 2
    widget.set_trial_list(trials, confirm_trial_change_with_user=False)
    # select first row
    for _ in range(3):
        QTest.keyClick(widget._widget_list_trials, Qt.Key_Up)
    assert widget.get_trial_list() == trials
    assert widget._widget_list_trials.count() == 3
    assert widget._widget_list_trials.currentRow() == 0
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is True
    assert widget._btn_move_up.isEnabled() is False
    assert widget._btn_move_down.isEnabled() is True
    assert widget._btn_remove.isEnabled() is True
    # select middle row
    QTest.keyClick(widget._widget_list_trials, Qt.Key_Down)
    assert widget.get_trial_list() == trials
    assert widget._widget_list_trials.count() == 3
    assert widget._widget_list_trials.currentRow() == 1
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is True
    assert widget._btn_move_up.isEnabled() is True
    assert widget._btn_move_down.isEnabled() is True
    assert widget._btn_remove.isEnabled() is True
    # select last row
    QTest.keyClick(widget._widget_list_trials, Qt.Key_Down)
    assert widget.get_trial_list() == trials
    assert widget._widget_list_trials.count() == 3
    assert widget._widget_list_trials.currentRow() == 2
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is True
    assert widget._btn_move_up.isEnabled() is True
    assert widget._btn_move_down.isEnabled() is False
    assert widget._btn_remove.isEnabled() is True
    # remove trial
    QTest.mouseClick(widget._btn_remove, Qt.MouseButton.LeftButton)
    QTest.keyClick(widget._widget_list_trials, Qt.Key_Down)
    assert widget.get_trial_list() == trials[0:2]
    assert widget._widget_list_trials.count() == 2
    assert widget._widget_list_trials.currentRow() == 1
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is True
    assert widget._btn_move_up.isEnabled() is True
    assert widget._btn_move_down.isEnabled() is False
    assert widget._btn_remove.isEnabled() is True
    # remove trial
    QTest.mouseClick(widget._btn_remove, Qt.MouseButton.LeftButton)
    QTest.keyClick(widget._widget_list_trials, Qt.Key_Down)
    assert widget.get_trial_list() == trials[0:1]
    assert widget._widget_list_trials.count() == 1
    assert widget._widget_list_trials.currentRow() == 0
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is True
    assert widget._btn_move_up.isEnabled() is False
    assert widget._btn_move_down.isEnabled() is False
    assert widget._btn_remove.isEnabled() is True
    # remove last trial
    QTest.mouseClick(widget._btn_remove, Qt.MouseButton.LeftButton)
    QTest.keyClick(widget._widget_list_trials, Qt.Key_Down)
    assert widget.get_trial_list() == []
    assert widget._widget_list_trials.count() == 0
    assert widget._btn_add.isEnabled() is True
    assert widget._btn_edit.isEnabled() is False
    assert widget._btn_move_up.isEnabled() is False
    assert widget._btn_move_down.isEnabled() is False
    assert widget._btn_remove.isEnabled() is False
