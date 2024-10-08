from __future__ import annotations

import gui_test_utils as gtu
import qt_test_utils as qtu
from psychopy.visual.window import Window
from pytest import approx
from qtpy import QtWidgets

import vstt
from vstt.experiment import Experiment
from vstt.meta_widget import MetadataWidget


def test_metadata_widget(window: Window) -> None:
    widget = MetadataWidget(parent=None, win=window)
    signal_received = qtu.SignalReceived(widget.experiment_modified)
    # default-constructed widget has a default experiment with default metadata
    assert widget.experiment.metadata == vstt.meta.default_metadata()
    assert widget.experiment.has_unsaved_changes is False
    assert not signal_received
    screenshot = gtu.call_target_and_get_screenshot(
        qtu.click,
        (widget._btn_preview_metadata,),
        window,
    )
    # most pixels are grey
    default_grey_pixel_fraction = gtu.pixel_color_fraction(screenshot, (128, 128, 128))
    assert 0.850 < default_grey_pixel_fraction < 0.999
    # a couple percent of black pixels due to black text
    assert 0.005 <= gtu.pixel_color_fraction(screenshot, (0, 0, 0)) <= 0.050
    experiment = Experiment()
    empty_metadata = vstt.meta.default_metadata()
    for key, value in empty_metadata.items():
        if isinstance(value, str):
            empty_metadata[key] = ""  # type: ignore
    empty_metadata["show_delay_countdown"] = False
    experiment.metadata = empty_metadata
    # assign experiment with empty metadata strings
    widget.experiment = experiment
    assert widget.experiment is experiment
    assert widget.experiment.metadata == empty_metadata
    assert widget.experiment.has_unsaved_changes is False
    assert not signal_received
    screenshot = gtu.call_target_and_get_screenshot(
        qtu.click,
        (widget._btn_preview_metadata,),
        window,
    )
    # all pixels grey except for blue continue text
    empty_grey_pixel_fraction = gtu.pixel_color_fraction(screenshot, (128, 128, 128))
    assert empty_grey_pixel_fraction > default_grey_pixel_fraction
    # no other text so no black pixels
    assert gtu.pixel_color_fraction(screenshot, (0, 0, 0)) == approx(0)
    # reset to experiment with empty metadata, then type variable name in each line edit
    assert widget.experiment.has_unsaved_changes is False
    assert widget.experiment.metadata == empty_metadata
    assert not signal_received
    for key in widget._str_widgets:
        line_edit = widget._str_widgets[key]
        assert line_edit is not None
        assert isinstance(line_edit, QtWidgets.QLineEdit)
        assert widget.experiment.metadata[key] == ""  # type: ignore
        signal_received.clear()
        qtu.press_keys(line_edit, key)
        assert widget.experiment.metadata[key] == key  # type: ignore
        assert widget.experiment.has_unsaved_changes is True
        assert signal_received
    for key, value in widget.experiment.metadata.items():
        if isinstance(value, str):
            assert value == key
    # assign another experiment to widget & update fields
    experiment2 = Experiment()
    experiment2.has_unsaved_changes = False
    widget.experiment = experiment2
    assert widget.experiment is experiment2
    assert widget.experiment.has_unsaved_changes is False
    for key, value in vstt.meta.default_metadata().items():
        if isinstance(value, str):
            line_edit = widget._str_widgets[key]
            signal_received.clear()
            assert line_edit is not None
            assert type(line_edit) is QtWidgets.QLineEdit
            assert widget.experiment.metadata[key] == value  # type: ignore
            qtu.press_keys(line_edit, "2")
            assert widget.experiment.metadata[key] == value + "2"  # type: ignore
            assert widget.experiment.has_unsaved_changes is True
            assert signal_received
    # experiment2 has been updated
    for key, value in experiment2.metadata.items():
        if isinstance(value, str):
            assert value == vstt.meta.default_metadata()[key] + "2"  # type: ignore
    # previous experiment was not modified
    for key, value in experiment.metadata.items():
        if isinstance(value, str):
            assert value == key
