from __future__ import annotations

import pytest
import qt_test_utils as qtu

# from PyQt5.uic.properties import QtWidgets
from psychopy.visual.window import Window
from qtpy import QtWidgets
from qtpy.QtTest import QTest

import vstt
from vstt.display import display_options_groups
from vstt.display import display_options_labels
from vstt.display_widget import DisplayOptionsWidget
from vstt.experiment import Experiment


@pytest.fixture
def widget(window: Window) -> DisplayOptionsWidget:
    widget = DisplayOptionsWidget(parent=None, win=window)
    # widget.show()
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
        assert widget.experiment.display_options[key] is False, f"failed key is:{key}"  # type: ignore
        qtu.press_space_key(check_box)
        QTest.qWait(200)
        assert widget.experiment.display_options[key] is True  # type: ignore
        assert widget.experiment.has_unsaved_changes is True
        assert signal_received
        signal_received.clear()
        qtu.press_space_key(check_box)
        assert widget.experiment.display_options[key] is False  # type: ignore
        assert signal_received
    # check that all values have the correct type
    for value in widget.experiment.display_options.values():
        assert isinstance(value, bool)


def test_group_in_tree_widget(widget: DisplayOptionsWidget) -> None:
    """
    test if the group title and labels of the TreeWidget items are in the expected groups and labels
    """
    tree_widget = widget.findChild(QtWidgets.QTreeWidget)
    assert tree_widget is not None

    expected_groups = display_options_groups()
    expected_labels = display_options_labels()

    # Collect actual group names from the TreeWidget
    actual_groups = [
        tree_widget.topLevelItem(i).text(0).strip()
        for i in range(tree_widget.topLevelItemCount())
        if tree_widget.topLevelItem(i).text(0).strip()
    ]

    # Ensure all group titles in the TreeWidget are in the expected groups
    for group in expected_groups:
        assert group in actual_groups

    # Collect actual labels from the TreeWidget items
    actual_labels = []
    for i in range(tree_widget.topLevelItemCount()):
        parent_item = tree_widget.topLevelItem(i)
        for j in range(parent_item.childCount()):
            child_item = parent_item.child(j)
            actual_labels.append(child_item.text(0).strip())
        if parent_item.childCount() == 0:
            actual_labels.append(parent_item.text(0).strip())

    # Ensure all labels from the TreeWidget items are in the expected labels
    for label in actual_labels:
        assert label in list(expected_labels.values())
