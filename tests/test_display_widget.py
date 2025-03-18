from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import qt_test_utils as qtu

# from PyQt5.uic.properties import QtWidgets
from psychopy.visual.window import Window
from pytestqt.qtbot import QtBot
from qtpy import QtCore
from qtpy import QtWidgets

import vstt
from vstt.display import display_options_labels
from vstt.display_widget import DisplayOptionsWidget
from vstt.experiment import Experiment


@pytest.fixture
def widget(window: Window) -> DisplayOptionsWidget:
    widget = DisplayOptionsWidget(parent=None, win=window)
    return widget


def test_display_options_widget(widget: DisplayOptionsWidget) -> None:
    signal_received = qtu.SignalReceived(widget.experiment_modified)
    # initially has default experiment with default display options
    assert widget.experiment.display_options == vstt.display.default_display_options()
    assert widget.experiment.has_unsaved_changes is False
    assert not signal_received
    # set an experiment with all options set to false
    experiment = Experiment()
    all_false = vstt.display.default_display_options()
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
        assert isinstance(value, bool)


def test_widget_initialization(widget: DisplayOptionsWidget) -> None:
    """
    test if widget initializes correctly.
    """
    assert widget is not None
    assert isinstance(widget, DisplayOptionsWidget)


def test_checkbox_created(widget: DisplayOptionsWidget) -> None:
    """
    test that checkboxes are created based on labels.
    """
    labels = display_options_labels()
    for key in labels:
        assert key in widget._widgets
        assert isinstance(widget._widgets[key], QtWidgets.QCheckBox)
        assert labels[key] == widget._widgets[key].text()


def test_checkbox_state_sync(widget: DisplayOptionsWidget) -> None:
    """
    test if checkboxes sync with the experiment's display options.
    """
    experiment = Experiment()
    experiment.display_options = {key: True for key in widget._widgets}  # type: ignore
    # for key in widget._widgets.keys():
    #     experiment.display_options[key] = True
    widget.experiment = experiment
    for key, checkbox in widget._widgets.items():
        assert checkbox.isChecked() == experiment.display_options[key]  # type: ignore


def test_checkbox_toggle_updates_experiment(
    widget: DisplayOptionsWidget, qtbot: QtBot
) -> None:
    """
    test if clicking the first checkbox updates experiment settings.
    """
    experiment = Experiment()
    experiment.display_options = {key: True for key in widget._widgets}  # type: ignore
    widget.experiment = experiment
    first_key = list(widget._widgets.keys())[0]
    first_checkbox = widget._widgets[first_key]
    initial_state = first_checkbox.isChecked()
    with qtbot.waitSignal(widget.experiment_modified, timeout=1000):
        qtbot.mouseClick(first_checkbox, QtCore.Qt.LeftButton)
    assert widget.experiment.display_options[first_key] != initial_state  # type: ignore


def test_experiment_modified_signal(widget: DisplayOptionsWidget, qtbot: QtBot) -> None:
    """
    test if experiment_modified signal is emitted on checkbox click.
    """
    first_key = list(widget._widgets.keys())[0]
    first_checkbox = widget._widgets[first_key]
    mock_callback = MagicMock()
    widget.experiment_modified.connect(mock_callback)
    qtbot.mouseClick(first_checkbox, QtCore.Qt.LeftButton)
    mock_callback.assert_called_once()
