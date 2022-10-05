import gui_test_utils as gtu
import motor_task_prototype.meta as mtpmeta
from motor_task_prototype.experiment import MotorTaskExperiment
from motor_task_prototype.meta_widget import MetadataWidget
from psychopy.visual.window import Window
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest


def test_metadata_widget(window: Window) -> None:
    widget = MetadataWidget(parent=None, win=window)
    signal_received = gtu.SignalReceived(widget.experiment_modified)
    # default-constructed widget has a default experiment with default metadata
    assert widget.experiment.metadata == mtpmeta.default_metadata()
    assert widget.experiment.has_unsaved_changes is True
    assert not signal_received
    screenshot = gtu.call_target_and_get_screenshot(
        QTest.mouseClick,
        (widget._btn_preview_metadata, Qt.MouseButton.LeftButton),
        window,
    )
    # most pixels are grey
    default_grey_pixel_fraction = gtu.pixel_color_fraction(screenshot, (128, 128, 128))
    assert 0.850 < default_grey_pixel_fraction < 0.999
    # a couple percent of black pixels due to black text
    assert 0.005 <= gtu.pixel_color_fraction(screenshot, (0, 0, 0)) <= 0.050
    experiment = MotorTaskExperiment()
    experiment.metadata = mtpmeta.empty_metadata()
    experiment.has_unsaved_changes = False
    # assign experiment with empty metadata
    widget.experiment = experiment
    assert widget.experiment is experiment
    assert widget.experiment.metadata == mtpmeta.empty_metadata()
    assert widget.experiment.has_unsaved_changes is False
    assert not signal_received
    screenshot = gtu.call_target_and_get_screenshot(
        QTest.mouseClick,
        (widget._btn_preview_metadata, Qt.MouseButton.LeftButton),
        window,
    )
    # all pixels grey except for blue continue text
    empty_grey_pixel_fraction = gtu.pixel_color_fraction(screenshot, (128, 128, 128))
    assert empty_grey_pixel_fraction > default_grey_pixel_fraction
    # no other text so no black pixels
    assert gtu.pixel_color_fraction(screenshot, (0, 0, 0)) == 0.000
    # reset to experiment with empty metadata, then type variable name in each line edit
    assert widget.experiment.has_unsaved_changes is False
    assert widget.experiment.metadata == mtpmeta.empty_metadata()
    assert not signal_received
    for key in mtpmeta.empty_metadata().keys():
        line_edit = widget._widgets[key]
        assert line_edit is not None
        assert type(line_edit) is QtWidgets.QLineEdit
        assert widget.experiment.metadata[key] == ""  # type: ignore
        signal_received.clear()
        QTest.keyClicks(line_edit, key)
        assert widget.experiment.metadata[key] == key  # type: ignore
        assert widget.experiment.has_unsaved_changes is True
        assert signal_received
    for key, value in widget.experiment.metadata.items():
        assert value == key
    # assign another experiment to widget & update fields
    experiment2 = MotorTaskExperiment()
    experiment2.has_unsaved_changes = False
    widget.experiment = experiment2
    assert widget.experiment is experiment2
    assert widget.experiment.has_unsaved_changes is False
    for key, value in mtpmeta.default_metadata().items():
        line_edit = widget._widgets[key]
        signal_received.clear()
        assert line_edit is not None
        assert type(line_edit) is QtWidgets.QLineEdit
        assert widget.experiment.metadata[key] == value  # type: ignore
        QTest.keyClicks(line_edit, "2")
        assert widget.experiment.metadata[key] == value + "2"  # type: ignore
        assert widget.experiment.has_unsaved_changes is True
        assert signal_received
    # experiment2 has been updated
    for key, value in experiment2.metadata.items():
        assert value == mtpmeta.default_metadata()[key] + "2"  # type: ignore
    # previous experiment was not modified
    for key, value in experiment.metadata.items():
        assert value == key
