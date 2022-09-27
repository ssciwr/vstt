from typing import Callable
from typing import Dict
from typing import Optional

from motor_task_prototype.display import default_display_options
from motor_task_prototype.display import display_options_labels
from motor_task_prototype.types import MotorTaskDisplayOptions
from PyQt5 import QtWidgets


class DisplayOptionsWidget(QtWidgets.QWidget):
    unsaved_changes: bool = False
    _options: MotorTaskDisplayOptions = default_display_options()
    _widgets: Dict[str, QtWidgets.QCheckBox] = {}

    def _update_value_callback(self, key: str) -> Callable[[bool], None]:
        def _update_value(value: bool) -> None:
            self._options[key] = value  # type: ignore
            self.unsaved_changes = True

        return _update_value

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        outer_layout = QtWidgets.QVBoxLayout()
        group_box = QtWidgets.QGroupBox("Display Options")
        outer_layout.addWidget(group_box)
        inner_layout = QtWidgets.QVBoxLayout()
        group_box.setLayout(inner_layout)
        labels = display_options_labels()
        for row_index, key in enumerate(default_display_options().keys()):
            checkbox = QtWidgets.QCheckBox(f"{labels[key]}", self)
            inner_layout.addWidget(checkbox)
            checkbox.clicked.connect(self._update_value_callback(key))
            self._widgets[key] = checkbox
        self.setLayout(outer_layout)
        self.unsaved_changes = False

    def set_display_options(self, display_options: MotorTaskDisplayOptions) -> None:
        self._options = display_options
        for key, widget in self._widgets.items():
            widget.setChecked(self._options[key])  # type: ignore
        self.unsaved_changes = False

    def get_display_options(self) -> MotorTaskDisplayOptions:
        return self._options
