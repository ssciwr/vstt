from typing import Callable
from typing import Dict
from typing import Optional

import motor_task_prototype.meta as mtpmeta
import motor_task_prototype.vis as mtpvis
from motor_task_prototype.experiment import MotorTaskExperiment
from psychopy.visual.window import Window
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt


class MetadataWidget(QtWidgets.QWidget):
    experiment_modified = QtCore.pyqtSignal()

    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        win: Optional[Window] = None,
        win_type: str = "pyglet",
    ):
        super().__init__(parent)
        self._win = win
        self._win_type = win_type
        self._experiment = MotorTaskExperiment()
        self._widgets: Dict[str, QtWidgets.QLineEdit] = {}

        group_box = QtWidgets.QGroupBox("Metadata")
        outer_layout = QtWidgets.QVBoxLayout()
        outer_layout.addWidget(group_box)
        inner_layout = QtWidgets.QVBoxLayout()
        group_box.setLayout(inner_layout)
        fields_layout = QtWidgets.QGridLayout()
        fields = QtWidgets.QWidget()
        fields.setLayout(fields_layout)
        labels = mtpmeta.metadata_labels()
        for row_index, key in enumerate(mtpmeta.default_metadata().keys()):
            lbl = QtWidgets.QLabel(f"{labels[key]}:", self)
            lbl.setAlignment(Qt.AlignRight)
            fields_layout.addWidget(lbl, row_index, 0)
            line_edit = QtWidgets.QLineEdit(self)
            fields_layout.addWidget(line_edit, row_index, 1)
            line_edit.textEdited.connect(self._update_value_callback(key))
            self._widgets[key] = line_edit
        inner_layout.addWidget(fields)
        self._btn_preview_metadata = QtWidgets.QPushButton("Preview Splash Screen")
        self._btn_preview_metadata.clicked.connect(self._btn_preview_metadata_clicked)
        inner_layout.addWidget(self._btn_preview_metadata)
        self.setLayout(outer_layout)

    def _update_value_callback(self, key: str) -> Callable[[str], None]:
        def _update_value(value: str) -> None:
            self._experiment.metadata[key] = value  # type: ignore
            self._experiment.has_unsaved_changes = True
            self.experiment_modified.emit()

        return _update_value

    def _btn_preview_metadata_clicked(self) -> None:
        mtpvis.splash_screen(
            self._experiment.metadata, win=self._win, win_type=self._win_type
        )

    @property
    def experiment(self) -> MotorTaskExperiment:
        return self._experiment

    @experiment.setter
    def experiment(self, experiment: MotorTaskExperiment) -> None:
        self._experiment = experiment
        for key, widget in self._widgets.items():
            widget.setText(self._experiment.metadata[key])  # type: ignore
