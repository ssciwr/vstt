from __future__ import annotations

from typing import Callable

from psychopy.visual.window import Window
from qtpy import QtCore
from qtpy import QtWidgets
from qtpy.QtGui import QFont

from vstt.display import display_options_groups
from vstt.display import display_options_labels
from vstt.experiment import Experiment


class DisplayOptionsWidget(QtWidgets.QWidget):
    experiment_modified = QtCore.Signal()

    def __init__(
        self, parent: QtWidgets.QWidget | None = None, win: Window | None = None
    ):
        super().__init__(parent)
        self._win = win
        self._experiment: Experiment = Experiment()
        self._widgets: dict[str, QtWidgets.QCheckBox] = {}

        # Main layout
        outer_layout = QtWidgets.QVBoxLayout()

        # Tree widget for collapsible categories
        tree_widget = QtWidgets.QTreeWidget()
        tree_widget.setHeaderHidden(True)  # Hide header
        outer_layout.addWidget(tree_widget)

        # Labels for display options
        labels = display_options_labels()
        collapsible_labels = display_options_groups()
        collapsible_keys = []

        # Add collapsible groups
        for group_title, keys in collapsible_labels.items():
            parent_item = QtWidgets.QTreeWidgetItem(tree_widget)
            parent_item.setText(0, group_title)
            parent_item.setFont(0, QFont("Arial", 11, QFont.Bold))

            for key in keys:
                collapsible_keys.append(key)
                if key in labels:
                    self._add_checkbox_to_tree_widget(
                        key, labels[key], parent_item, tree_widget
                    )

        # Add non-collapsible options
        for key, label in labels.items():
            if key not in collapsible_keys:
                self._add_checkbox_to_tree_widget(key, label, tree_widget, tree_widget)

        self.setLayout(outer_layout)

    def _add_checkbox_to_tree_widget(
        self,
        key: str,
        label: str,
        parent_item: QtWidgets.QTreeWidgetItem | QtWidgets.QTreeWidget,
        tree_widget: QtWidgets.QTreeWidget,
    ) -> None:
        child_item = QtWidgets.QTreeWidgetItem(parent_item)
        child_item.setText(
            0, "    " + label
        )  # set text explicitly so that text can be obtained in the test cases
        checkbox = QtWidgets.QCheckBox()
        tree_widget.setItemWidget(child_item, 0, checkbox)
        checkbox.clicked.connect(self._update_value_callback(key))
        self._widgets[key] = checkbox

    def _update_value_callback(self, key: str) -> Callable[[bool], None]:
        def _update_value(value: bool) -> None:
            self._experiment.display_options[key] = value  # type: ignore
            self._experiment.has_unsaved_changes = True
            self.experiment_modified.emit()

        return _update_value

    @property
    def experiment(self) -> Experiment:
        return self._experiment

    @experiment.setter
    def experiment(self, experiment: Experiment) -> None:
        self._experiment = experiment
        for key, widget in self._widgets.items():
            widget.setChecked(self._experiment.display_options[key])  # type: ignore
