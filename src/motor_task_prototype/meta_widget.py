from typing import Callable
from typing import Dict
from typing import Optional

import motor_task_prototype.meta as mtpmeta
import motor_task_prototype.vis as mtpvis
from motor_task_prototype.types import MotorTaskMetadata
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt


class MetadataWidget(QtWidgets.QWidget):
    unsaved_changes: bool = False
    _meta: MotorTaskMetadata = mtpmeta.empty_metadata()
    _widgets: Dict[str, QtWidgets.QLineEdit] = {}

    def _update_value_callback(self, key: str) -> Callable[[str], None]:
        def _update_value(value: str) -> None:
            self._meta[key] = value  # type: ignore
            self.unsaved_changes = True

        return _update_value

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
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
        btn_preview_metadata = QtWidgets.QPushButton("Preview Splash Screen")
        btn_preview_metadata.clicked.connect(self._btn_preview_metadata_clicked)
        inner_layout.addWidget(btn_preview_metadata)
        self.setLayout(outer_layout)
        self.unsaved_changes = False

    def _btn_preview_metadata_clicked(self) -> None:
        mtpvis.splash_screen(self._meta)

    def set_metadata(self, metadata: MotorTaskMetadata) -> None:
        self._meta = metadata
        for key, widget in self._widgets.items():
            widget.setText(self._meta[key])  # type: ignore
        self.unsaved_changes = False

    def get_metadata(self) -> MotorTaskMetadata:
        return self._meta
