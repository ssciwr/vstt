from __future__ import annotations

from typing import Any
from typing import List
from typing import Optional

import qtpy
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy.QtCore import Qt
from qtpy.QtTest import QTest


# send key clicks to a widget
def press_keys(widget: QtWidgets.QWidget, text: str) -> None:
    QTest.keyClicks(widget, text)


# send key clicks to a widget
def press_key(widget: QtWidgets.QWidget, key: str) -> None:
    QTest.keyClick(widget, key)


# send keyboard up key click to a widget
def press_up_key(widget: QtWidgets.QWidget) -> None:
    QTest.keyClick(widget, Qt.Key_Up)


# send keyboard down key click to a widget
def press_down_key(widget: QtWidgets.QWidget) -> None:
    QTest.keyClick(widget, Qt.Key_Down)


# click on a widget
def click(
    widget: QtWidgets.QWidget, button: Qt.MouseButton = Qt.MouseButton.LeftButton
) -> None:
    QTest.mouseClick(widget, button)


# class to receive a pyqt signal
class SignalReceived:
    def __init__(self, signal: Any):
        self._signal_received = False
        signal.connect(self._receive)

    def __bool__(self) -> bool:
        return self._signal_received

    def _receive(self) -> None:
        self._signal_received = True

    def clear(self) -> None:
        self._signal_received = False


# Class for interacting with modal widgets (partial python port of MIT-licensed C++ code from sme)
# https://github.com/spatial-model-editor/spatial-model-editor/blob/main/test/test_utils/qt_test_utils.hpp
class ModalWidgetTimer:
    def __init__(
        self,
        keys: List[str],
        start_after: Optional[ModalWidgetTimer] = None,
    ) -> None:
        self._keys = keys
        if start_after is not None:
            start_after._other_mwt_to_start = self
        self._other_mwt_to_start: Optional[ModalWidgetTimer] = None
        self._timer = QtCore.QTimer()
        self._widget_to_ignore: Optional[QtWidgets.QWidget] = None
        self._timeout = 30000
        self._timer.timeout.connect(self._send_keys)
        self._widget_type: str = ""
        self._widget_text: str = ""

    def _save_widget_info(self, widget: QtWidgets.QWidget) -> None:
        self._widget_type = widget.__class__.__name__
        if isinstance(widget, QtWidgets.QFileDialog):
            for mode in ["Open", "Save"]:
                if widget.acceptMode() == getattr(
                    QtWidgets.QFileDialog.AcceptMode, f"Accept{mode}"
                ):
                    self._widget_type += f".{mode}"
            print(
                f"ModalWidgetTimer ::   - {widget.selectedNameFilter()} / {widget.nameFilters()}",
                flush=True,
            )
            print(f"ModalWidgetTimer ::   - {widget.selectedFiles()}", flush=True)
        if isinstance(widget, QtWidgets.QMessageBox):
            self._widget_text = widget.text()
            print(f"ModalWidgetTimer ::   - {widget.text()}", flush=True)
        else:
            self._widget_text = widget.windowTitle()
            print(f"ModalWidgetTimer ::   - {widget.windowTitle()}", flush=True)

    def _send_keys(self) -> None:
        widget = QtWidgets.QApplication.activeModalWidget()
        self._timeout -= self._timer.interval()
        if self._timeout < 0:
            raise RuntimeError("ModalWidgetTimer :: Timeout waiting for modal widget")
        if widget is None or widget is self._widget_to_ignore:
            return
        if self._other_mwt_to_start is not None:
            print(
                f"\nModalWidgetTimer :: starting {self._other_mwt_to_start}", flush=True
            )
            self._other_mwt_to_start._widget_to_ignore = widget
            self._other_mwt_to_start.start()
        print(f"\nModalWidgetTimer :: Found {widget}", flush=True)
        self._save_widget_info(widget)
        for key in self._keys:
            key_seq = QtGui.QKeySequence(key)
            str_key = key_seq.toString()
            if qtpy.QT6:
                qt_key = key_seq[0].key()
            else:
                qt_key = Qt.Key(key_seq[0])
            print(
                f"ModalWidgetTimer ::   - sending '{str_key} [{qt_key}]' to {widget}",
                flush=True,
            )
            QTest.keyClick(widget, qt_key)
        self._timer.stop()

    def start(self, timer_interval: int = 100, timeout: int = 30000) -> None:
        self._timeout = timeout
        self._timer.start(timer_interval)

    @property
    def widget_type(self) -> str:
        return self._widget_type

    @property
    def widget_text(self) -> str:
        return self._widget_text
