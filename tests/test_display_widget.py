from typing import Dict

import motor_task_prototype.display as mtpdisplay
from motor_task_prototype.display_widget import DisplayOptionsWidget
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest


def _get_check_boxes(
    display_options_widget: DisplayOptionsWidget,
) -> Dict[str, QtWidgets.QCheckBox]:
    check_boxes = {}
    labels = {v: k for k, v in mtpdisplay.display_options_labels().items()}
    for check_box in display_options_widget.findChildren(QtWidgets.QCheckBox):
        check_boxes[labels[check_box.text()]] = check_box
    return check_boxes


def test_display_options_widget() -> None:
    widget = DisplayOptionsWidget(None)
    # initially has default display options
    assert widget.get_display_options() == mtpdisplay.default_display_options()
    # set all to false
    all_false = mtpdisplay.default_display_options()
    for key in all_false:
        all_false[key] = False  # type: ignore
    widget.set_display_options(all_false)
    assert widget.get_display_options() == all_false
    # modify options by clicking on each check box in turn
    for key, check_box in _get_check_boxes(widget).items():
        assert widget.get_display_options()[key] is False  # type: ignore
        QTest.mouseClick(check_box, Qt.MouseButton.LeftButton)
        assert widget.get_display_options()[key] is True  # type: ignore
        QTest.mouseClick(check_box, Qt.MouseButton.LeftButton)
        assert widget.get_display_options()[key] is False  # type: ignore
    # check that all values have the correct type
    for value in widget.get_display_options().values():
        assert type(value) is bool
