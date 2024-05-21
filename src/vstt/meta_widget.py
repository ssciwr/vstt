from __future__ import annotations

from typing import Callable

from psychopy.visual.window import Window
from qtpy import QtCore
from qtpy import QtWidgets
from qtpy.QtCore import Qt

from vstt.experiment import Experiment
from vstt.meta import default_metadata
from vstt.meta import metadata_labels
from vstt.vis import splash_screen


class MetadataWidget(QtWidgets.QWidget):
    experiment_modified = QtCore.Signal()

    def __init__(
        self, parent: QtWidgets.QWidget | None = None, win: Window | None = None
    ):
        super().__init__(parent)
        self._win = win
        self._experiment = Experiment()
        self._str_widgets: dict[str, QtWidgets.QLineEdit] = {}
        self._bool_widgets: dict[str, QtWidgets.QCheckBox] = {}
        self._float_widgets: dict[str, QtWidgets.QDoubleSpinBox] = {}

        outer_layout = QtWidgets.QVBoxLayout()
        group_box = QtWidgets.QGroupBox("Metadata")
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(group_box)
        outer_layout.addWidget(scroll_area)
        inner_layout = QtWidgets.QVBoxLayout()
        group_box.setLayout(inner_layout)
        fields_layout = QtWidgets.QGridLayout()
        fields = QtWidgets.QWidget()
        fields.setLayout(fields_layout)
        labels = metadata_labels()
        for row_index, (key, value) in enumerate(default_metadata().items()):
            if isinstance(value, str):
                lbl = QtWidgets.QLabel(f"{labels[key]}:", self)
                lbl.setAlignment(Qt.AlignRight)
                fields_layout.addWidget(lbl, row_index, 0)
                line_edit = QtWidgets.QLineEdit(self)
                fields_layout.addWidget(line_edit, row_index, 1)
                line_edit.textEdited.connect(self._update_value_callback(key))
                self._str_widgets[key] = line_edit
            elif isinstance(value, bool):
                checkbox = QtWidgets.QCheckBox(f"{labels[key]}", self)
                fields_layout.addWidget(checkbox, row_index, 1)
                checkbox.clicked.connect(self._update_value_callback(key))
                self._bool_widgets[key] = checkbox
            elif isinstance(value, (int, float)):
                lbl = QtWidgets.QLabel(f"{labels[key]}:", self)
                lbl.setAlignment(Qt.AlignRight)
                fields_layout.addWidget(lbl, row_index, 0)
                spinbox = QtWidgets.QDoubleSpinBox(self)
                fields_layout.addWidget(spinbox, row_index, 1)
                spinbox.valueChanged.connect(self._update_value_callback(key))
                self._float_widgets[key] = spinbox

        inner_layout.addWidget(fields)
        self._btn_preview_metadata = QtWidgets.QPushButton("Preview Splash Screen")
        self._btn_preview_metadata.clicked.connect(self._btn_preview_metadata_clicked)
        inner_layout.addWidget(self._btn_preview_metadata)
        self.setLayout(outer_layout)

    def _update_value_callback(self, key: str) -> Callable[[str | bool | float], None]:
        def _update_value(value: str | bool | float) -> None:
            if value != self._experiment.metadata[key]:  # type: ignore
                self._experiment.metadata[key] = value  # type: ignore
                self._experiment.has_unsaved_changes = True
                self.experiment_modified.emit()

        return _update_value

    def _btn_preview_metadata_clicked(self) -> None:
        splash_screen(
            display_time_seconds=self._experiment.metadata["display_duration"],
            enter_to_skip_delay=self._experiment.metadata["enter_to_skip_delay"],
            show_delay_countdown=self._experiment.metadata["show_delay_countdown"],
            metadata=self._experiment.metadata,
            win=self._win,
        )

    @property
    def experiment(self) -> Experiment:
        return self._experiment

    @experiment.setter
    def experiment(self, experiment: Experiment) -> None:
        self._experiment = experiment
        for key, str_widget in self._str_widgets.items():
            str_widget.setText(self._experiment.metadata[key])  # type: ignore
        for key, bool_widget in self._bool_widgets.items():
            bool_widget.setChecked(self._experiment.metadata[key])  # type: ignore
        for key, float_widget in self._float_widgets.items():
            float_widget.setValue(self._experiment.metadata[key])  # type: ignore
