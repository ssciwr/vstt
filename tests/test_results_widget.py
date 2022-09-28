from motor_task_prototype.results_widget import ResultsWidget
from psychopy.data import TrialHandlerExt
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest


def test_results_widget(
    experiment_no_results: TrialHandlerExt, experiment_with_results: TrialHandlerExt
) -> None:
    widget = ResultsWidget(None)
    # initially empty
    assert widget.have_results() is False
    assert widget._list_trials.count() == 0
    assert widget._btn_display_trial.isEnabled() is False
    assert widget._btn_display_condition.isEnabled() is False
    # assign experiment without results
    widget.set_results(experiment_no_results)
    assert widget.have_results() is False
    assert widget._list_trials.count() == 0
    assert widget._btn_display_trial.isEnabled() is False
    assert widget._btn_display_condition.isEnabled() is False
    # assign experiment with results
    widget.set_results(experiment_with_results)
    n_trials = 4
    assert widget.have_results() is True
    assert widget._list_trials.count() == n_trials
    for _ in range(n_trials):
        QTest.keyClick(widget._list_trials, Qt.Key_Up)
    assert widget._list_trials.currentRow() == 0
    for row in range(n_trials):
        assert widget._list_trials.currentRow() == row
        assert widget._btn_display_trial.isEnabled() is True
        assert widget._btn_display_condition.isEnabled() is True
        QTest.keyClick(widget._list_trials, Qt.Key_Down)
    assert widget._list_trials.currentRow() == n_trials - 1
    # clear results
    widget.clear_results()
    assert widget.have_results() is False
    assert widget._list_trials.count() == 0
    assert widget._btn_display_trial.isEnabled() is False
    assert widget._btn_display_condition.isEnabled() is False
