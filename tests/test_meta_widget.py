import gui_test_utils as gtu
import motor_task_prototype.meta as mtpmeta
from motor_task_prototype.meta_widget import MetadataWidget
from psychopy.visual.window import Window
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest


def test_metadata_widget(window: Window) -> None:
    widget = MetadataWidget(parent=None, win=window)
    # initially has empty metadata
    assert widget.get_metadata() == mtpmeta.empty_metadata()
    assert widget.unsaved_changes is False
    screenshot = gtu.call_target_and_get_screenshot(
        QTest.mouseClick,
        (widget._btn_preview_metadata, Qt.MouseButton.LeftButton),
        window,
    )
    # all pixels grey except for blue continue text
    empty_grey_pixel_fraction = gtu.pixel_color_fraction(screenshot, (128, 128, 128))
    assert 0.990 < empty_grey_pixel_fraction < 0.999
    # no other text so no black pixels
    assert gtu.pixel_color_fraction(screenshot, (0, 0, 0)) == 0.000
    # set all to defaults
    widget.set_metadata(mtpmeta.default_metadata())
    assert widget.get_metadata() == mtpmeta.default_metadata()
    assert widget.unsaved_changes is False
    screenshot = gtu.call_target_and_get_screenshot(
        QTest.mouseClick,
        (widget._btn_preview_metadata, Qt.MouseButton.LeftButton),
        window,
    )
    # less grey pixels since we now have black text
    assert (
        gtu.pixel_color_fraction(screenshot, (128, 128, 128))
        < empty_grey_pixel_fraction
    )
    # a couple percent of black pixels due to black text
    assert 0.005 <= gtu.pixel_color_fraction(screenshot, (0, 0, 0)) <= 0.050
    # reset to empty, then type in each line edit
    widget.set_metadata(mtpmeta.empty_metadata())
    assert widget.unsaved_changes is False
    for key in mtpmeta.empty_metadata().keys():
        line_edit = widget._widgets[key]
        assert line_edit is not None
        assert type(line_edit) is QtWidgets.QLineEdit
        assert widget.get_metadata()[key] == ""  # type: ignore
        QTest.keyClicks(line_edit, key)
        assert widget.get_metadata()[key] == key  # type: ignore
        assert widget.unsaved_changes is True
    for key, value in widget.get_metadata().items():
        assert value == key
