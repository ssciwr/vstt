from __future__ import annotations

import motor_task_prototype.display as mtpdisplay
import qt_test_utils as qtu
from motor_task_prototype.display_widget import DisplayOptionsWidget
from motor_task_prototype.experiment import MotorTaskExperiment
from psychopy.visual.window import Window


def test_display_options_widget(window: Window) -> None:
    widget = DisplayOptionsWidget(parent=None, win=window)
    signal_received = qtu.SignalReceived(widget.experiment_modified)
    # initially has default experiment with default display options
    assert widget.experiment.display_options == mtpdisplay.default_display_options()
    assert widget.experiment.has_unsaved_changes is False
    assert not signal_received
    # set an experiment with all options set to false
    experiment = MotorTaskExperiment()
    all_false = mtpdisplay.default_display_options()
    for key in all_false:
        all_false[key] = False  # type: ignore
    experiment.display_options = all_false
    widget.experiment = experiment
    assert widget.experiment is experiment
    assert widget.experiment.display_options == all_false
    assert widget.experiment.has_unsaved_changes is False
    assert not signal_received
    # modify options by clicking on each check box in turn
    for key, check_box in widget._widgets.items():
        signal_received.clear()
        assert widget.experiment.display_options[key] is False  # type: ignore
        qtu.click(check_box)
        assert widget.experiment.display_options[key] is True  # type: ignore
        assert widget.experiment.has_unsaved_changes is True
        assert signal_received
        signal_received.clear()
        qtu.click(check_box)
        assert widget.experiment.display_options[key] is False  # type: ignore
        assert signal_received
    # check that all values have the correct type
    for value in widget.experiment.display_options.values():
        assert type(value) is bool
