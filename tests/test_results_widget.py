from __future__ import annotations

import gui_test_utils as gtu
from motor_task_prototype.experiment import MotorTaskExperiment
from motor_task_prototype.results_widget import ResultsWidget
from psychopy.visual.window import Window
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest


def test_results_widget_no_experiment(window: Window) -> None:
    widget = ResultsWidget(parent=None, win=window)
    # initially empty
    assert widget.experiment.trial_handler_with_results is None
    assert widget._list_trials.count() == 0
    assert widget._btn_display_trial.isEnabled() is False
    assert widget._btn_display_condition.isEnabled() is False


def test_results_widget_experiment_no_results(
    experiment_no_results: MotorTaskExperiment, window: Window
) -> None:
    widget = ResultsWidget(parent=None, win=window)
    # assign experiment without results
    widget.experiment = experiment_no_results
    assert widget.experiment.trial_handler_with_results is None
    assert widget._list_trials.count() == 0
    assert widget._btn_display_trial.isEnabled() is False
    assert widget._btn_display_condition.isEnabled() is False


def test_results_widget_experiment_with_results(
    experiment_with_results: MotorTaskExperiment, window: Window
) -> None:
    widget = ResultsWidget(parent=None, win=window)
    # assign experiment with results
    widget.experiment = experiment_with_results
    n_trials = 4
    assert widget.experiment.trial_handler_with_results is not None
    assert widget.experiment.trial_handler_with_results.nTotal == n_trials
    assert widget._list_trials.count() == n_trials
    # select first row
    for _ in range(n_trials):
        QTest.keyClick(widget._list_trials, Qt.Key_Up)
    assert widget._list_trials.currentRow() == 0
    # display trial results
    screenshot = gtu.call_target_and_get_screenshot(
        QTest.mouseClick,
        (widget._btn_display_trial, Qt.MouseButton.LeftButton),
        window,
    )
    # most pixels grey
    trial_grey_frac = gtu.pixel_color_fraction(screenshot, (128, 128, 128))
    assert 0.900 < trial_grey_frac < 0.999
    # some off-white pixels
    assert 0.001 <= gtu.pixel_color_fraction(screenshot, (240, 248, 255)) <= 0.050
    # display condition results from 3 trials
    screenshot = gtu.call_target_and_get_screenshot(
        QTest.mouseClick,
        (widget._btn_display_condition, Qt.MouseButton.LeftButton),
        window,
    )
    # less grey pixels than a single trial
    assert gtu.pixel_color_fraction(screenshot, (128, 128, 128)) < trial_grey_frac
    # some off-white pixels
    assert 0.001 <= gtu.pixel_color_fraction(screenshot, (240, 248, 255)) <= 0.050
    # select each row in turn
    for row in range(n_trials):
        assert widget._list_trials.currentRow() == row
        assert widget._btn_display_trial.isEnabled() is True
        assert widget._btn_display_condition.isEnabled() is True
        QTest.keyClick(widget._list_trials, Qt.Key_Down)
    assert widget._list_trials.currentRow() == n_trials - 1
    # assign a new experiment without results
    experiment_with_results.clear_results()
    widget.experiment = experiment_with_results
    assert widget.experiment.trial_handler_with_results is None
    assert widget._list_trials.count() == 0
    assert widget._btn_display_trial.isEnabled() is False
    assert widget._btn_display_condition.isEnabled() is False
