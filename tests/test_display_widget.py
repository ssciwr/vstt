import gui_test_utils as gtu
import motor_task_prototype.display as mtpdisplay
from motor_task_prototype.display_widget import DisplayOptionsWidget
from motor_task_prototype.experiment import MotorTaskExperiment
from psychopy.visual.window import Window
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest


def test_display_options_widget(window: Window) -> None:
    widget = DisplayOptionsWidget(parent=None, win=window)
    signal_received = gtu.SignalReceived(widget.experiment_modified)
    # initially has default experiment with default display options
    assert widget.experiment.display_options == mtpdisplay.default_display_options()
    assert widget.experiment.has_unsaved_changes is True
    assert not signal_received
    # set an experiment with all options set to false
    experiment = MotorTaskExperiment()
    all_false = mtpdisplay.default_display_options()
    for key in all_false:
        all_false[key] = False  # type: ignore
    experiment.display_options = all_false
    experiment.has_unsaved_changes = False
    widget.experiment = experiment
    assert widget.experiment is experiment
    assert widget.experiment.display_options == all_false
    assert widget.experiment.has_unsaved_changes is False
    assert not signal_received
    # modify options by clicking on each check box in turn
    for key, check_box in widget._widgets.items():
        signal_received.clear()
        assert widget.experiment.display_options[key] is False  # type: ignore
        QTest.mouseClick(check_box, Qt.MouseButton.LeftButton)
        assert widget.experiment.display_options[key] is True  # type: ignore
        assert widget.experiment.has_unsaved_changes is True
        assert signal_received
        signal_received.clear()
        QTest.mouseClick(check_box, Qt.MouseButton.LeftButton)
        QTest.qWait(100)
        assert widget.experiment.display_options[key] is False  # type: ignore
        assert signal_received
    # check that all values have the correct type
    for value in widget.experiment.display_options.values():
        assert type(value) is bool
