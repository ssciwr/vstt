from typing import Callable
from typing import Dict

from motor_task_prototype.display import default_display_options
from motor_task_prototype.display import display_options_labels
from motor_task_prototype.types import MotorTaskDisplayOptions
from PyQt5 import QtWidgets


class DisplayOptionsWidget(QtWidgets.QWidget):
    options: MotorTaskDisplayOptions = default_display_options()
    widgets: Dict[str, QtWidgets.QCheckBox] = {}
    unsaved_changes: bool = False

    def update_value_callback(self, key: str) -> Callable[[bool], None]:
        def update_value(value: bool) -> None:
            self.options[key] = value  # type: ignore
            self.unsaved_changes = True

        return update_value

    def __init__(self, parent: QtWidgets.QWidget):
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
            checkbox.stateChanged.connect(self.update_value_callback(key))
            self.widgets[key] = checkbox
        self.setLayout(outer_layout)
        self.unsaved_changes = False

    def set_display_options(self, display_options: MotorTaskDisplayOptions) -> None:
        self.options = display_options
        for key, widget in self.widgets.items():
            widget.setChecked(self.options[key])  # type: ignore
        self.unsaved_changes = False

    def get_display_options(self) -> MotorTaskDisplayOptions:
        return self.options
