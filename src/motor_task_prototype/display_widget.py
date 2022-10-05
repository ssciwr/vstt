from __future__ import annotations

from typing import Callable
from typing import Dict
from typing import Optional

from motor_task_prototype.display import display_options_labels
from motor_task_prototype.experiment import MotorTaskExperiment
from psychopy.visual.window import Window
from PyQt5 import QtCore
from PyQt5 import QtWidgets


class DisplayOptionsWidget(QtWidgets.QWidget):
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
        self._experiment: MotorTaskExperiment = MotorTaskExperiment()
        self._widgets: Dict[str, QtWidgets.QCheckBox] = {}

        outer_layout = QtWidgets.QVBoxLayout()
        group_box = QtWidgets.QGroupBox("Display Options")
        outer_layout.addWidget(group_box)
        inner_layout = QtWidgets.QVBoxLayout()
        group_box.setLayout(inner_layout)
        labels = display_options_labels()
        for row_index, key in enumerate(labels.keys()):
            checkbox = QtWidgets.QCheckBox(f"{labels[key]}", self)
            inner_layout.addWidget(checkbox)
            checkbox.clicked.connect(self._update_value_callback(key))
            self._widgets[key] = checkbox
        self.setLayout(outer_layout)

    def _update_value_callback(self, key: str) -> Callable[[bool], None]:
        def _update_value(value: bool) -> None:
            self._experiment.display_options[key] = value  # type: ignore
            self._experiment.has_unsaved_changes = True
            self.experiment_modified.emit()

        return _update_value

    @property
    def experiment(self) -> MotorTaskExperiment:
        return self._experiment

    @experiment.setter
    def experiment(self, experiment: MotorTaskExperiment) -> None:
        self._experiment = experiment
        for key, widget in self._widgets.items():
            widget.setChecked(self._experiment.display_options[key])  # type: ignore
