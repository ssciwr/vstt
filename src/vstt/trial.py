from __future__ import annotations

import copy
from typing import Any
from typing import Mapping

import numpy as np
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QTreeWidget
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from vstt.common import import_typed_dict
from vstt.vtypes import Trial


def describe_trial(trial: Trial) -> str:
    repeats = f"{trial['weight']} repeat{'s' if trial['weight'] > 1 else ''}"
    targets = f"target{'s' if trial['num_targets'] > 1 else ''}"
    if trial["condition_timeout"] > 0.0:
        repeats = f"up to {repeats}"
        targets = f"{targets} in {trial['condition_timeout']}s"
    return f"{repeats} of {trial['num_targets']} {trial['target_order']} {targets}"


def describe_trials(trials: list[Trial]) -> str:
    return "\n".join(["  - " + describe_trial(trial) for trial in trials])


def default_trial() -> Trial:
    return {
        "weight": 1,
        "condition_timeout": 0.0,
        "num_targets": 8,
        "target_order": "clockwise",
        "target_indices": "0 1 2 3 4 5 6 7",
        "add_central_target": True,
        "hide_target_when_reached": True,
        "turn_target_to_green_when_reached": False,
        "show_target_labels": False,
        "target_labels": "0 1 2 3 4 5 6 7",
        "fixed_target_intervals": False,
        "target_duration": 5.0,
        "central_target_duration": 5.0,
        "pre_target_delay": 0.0,
        "pre_central_target_delay": 0.0,
        "pre_first_target_extra_delay": 0.0,
        "target_distance": 0.4,
        "target_size": 0.04,
        "central_target_size": 0.02,
        "show_inactive_targets": True,
        "ignore_incorrect_targets": True,
        "play_sound": True,
        "use_joystick": False,
        "joystick_max_speed": 0.02,
        "show_cursor": True,
        "cursor_size": 0.02,
        "show_cursor_path": True,
        "automove_cursor_to_center": False,
        "freeze_cursor_between_targets": False,
        "cursor_rotation_degrees": 0.0,
        "post_trial_delay": 0.0,
        "post_trial_display_results": False,
        "post_block_delay": 10.0,
        "post_block_display_results": True,
        "show_delay_countdown": True,
        "enter_to_skip_delay": True,
    }


def trial_labels() -> dict:
    return {
        "weight": "Repetitions",
        "condition_timeout": "Maximum time, 0=unlimited (secs)",
        "num_targets": "Number of targets",
        "target_order": "Target order",
        "target_indices": "Target indices",
        "add_central_target": "Add a central target",
        "hide_target_when_reached": "Hide target when reached",
        "turn_target_to_green_when_reached": "Turn target to green when reached",
        "show_target_labels": "Display target labels",
        "target_labels": "Target labels",
        "fixed_target_intervals": "Fixed target display intervals",
        "target_duration": "Target display duration (secs)",
        "central_target_duration": "Central target display duration (secs)",
        "pre_target_delay": "Delay before outer target display (secs)",
        "pre_central_target_delay": "Delay before central target display (secs)",
        "pre_first_target_extra_delay": "Extra delay before first outer target of condition (secs)",
        "target_distance": "Distance to targets (screen height fraction)",
        "target_size": "Target size (screen height fraction)",
        "central_target_size": "Central target size (screen height fraction)",
        "show_inactive_targets": "Show inactive targets",
        "ignore_incorrect_targets": "Ignore cursor hitting incorrect target",
        "play_sound": "Play a sound on target display",
        "use_joystick": "Control the cursor using a joystick",
        "joystick_max_speed": "Maximum joystick speed (screen height fraction per frame)",
        "show_cursor": "Show cursor",
        "cursor_size": "Cursor size (screen height fraction)",
        "show_cursor_path": "Show cursor path",
        "automove_cursor_to_center": "Automatically move cursor to center",
        "freeze_cursor_between_targets": "Freeze cursor until target is displayed",
        "cursor_rotation_degrees": "Cursor rotation (degrees)",
        "post_trial_delay": "Delay between trials (secs)",
        "post_trial_display_results": "Display results after each trial",
        "post_block_delay": "Delay after last trial (secs)",
        "post_block_display_results": "Display combined results after last trial",
        "show_delay_countdown": "Display a countdown during delays",
        "enter_to_skip_delay": "Skip delay by pressing enter key",
    }


def trial_groups() -> dict[str, list[str]]:
    return {
        "Target Settings:": [
            "num_targets",
            "target_order",
            "target_indices",
            "add_central_target",
            "hide_target_when_reached",
            "turn_target_to_green_when_reached",
            "show_target_labels",
            "target_labels",
            "fixed_target_intervals",
            "target_duration",
            "central_target_duration",
            "pre_target_delay",
            "pre_central_target_delay",
            "pre_first_target_extra_delay",
            "target_distance",
            "target_size",
            "central_target_size",
            "show_inactive_targets",
            "ignore_incorrect_targets",
        ],
    }


class TreeDialog(QDialog):
    def __init__(self, trial: Trial):
        super().__init__()
        self.setWindowTitle("Trial Conditions")
        self.tree_layout = QVBoxLayout(self)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)  # Hide header for cleaner UI
        self.trial = trial

        # fix layout size
        self.setFixedSize(600, 800)

        # Populate the QTreeWidget with categories and settings
        collapsible_keys = []
        for category, items in trial_groups().items():
            parent_item = QTreeWidgetItem(self.tree_widget)
            parent_item.setText(0, category)
            parent_item.setFont(0, QFont("Arial", 11, QFont.Bold))

            for key in items:
                label = trial_labels()[key]
                collapsible_keys.append(key)
                value = self.trial[key]  # type: ignore
                child_item = QTreeWidgetItem(parent_item)

                # Create a label + input widget for every setting
                widget = self._create_labeled_widget(label, key, value)
                self.tree_widget.setItemWidget(child_item, 0, widget)
        for key, label in trial_labels().items():
            if key not in collapsible_keys:
                item = QTreeWidgetItem(self.tree_widget)
                value = self.trial[key]  # type: ignore
                # Create an appropriate input widget for each setting
                widget = self._create_labeled_widget(label, key, value)
                self.tree_widget.setItemWidget(item, 0, widget)

        self.tree_layout.addWidget(self.tree_widget)

        # OK and Cancel buttons
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.tree_layout.addWidget(self.ok_button)
        self.tree_layout.addWidget(self.cancel_button)

    def _create_labeled_widget(
        self, label_text: str, key: str, value: bool | str | int | float
    ) -> QWidget:
        """
        Creates a container widget with a label on the left and an input widget on the right.
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove extra margins

        # Create label and input widget
        label = QLabel(label_text)
        input_widget = self._create_input_widget(label_text, key, value)

        # Add label and input widget to the layout
        if not isinstance(value, bool):  # put checkbox in front of the label
            layout.addWidget(label)
        layout.addWidget(input_widget)
        layout.addStretch()  # Add stretch to align everything neatly
        return container

    def _create_input_widget(
        self, label_text: str, key: str, value: bool | str | int | float
    ) -> QCheckBox | QSpinBox | QDoubleSpinBox | QComboBox | QLineEdit:
        """Creates an input widget based on the type of value."""
        widget: QCheckBox | QComboBox | QSpinBox | QDoubleSpinBox | QLineEdit
        if isinstance(value, bool):
            widget = QCheckBox(f"{label_text}")
            widget.setChecked(value)
            widget.stateChanged.connect(lambda val: self._update_trial(key, val))
        elif isinstance(value, int):
            widget = QSpinBox()
            widget.setValue(value)
            widget.valueChanged.connect(lambda val: self._update_trial(key, val))
        elif isinstance(value, float):
            widget = QDoubleSpinBox()
            widget.setValue(value)
            widget.setDecimals(2)
            widget.valueChanged.connect(lambda val: self._update_trial(key, val))
        elif key == "target_order":
            widget = QComboBox()
            options = ["clockwise", "anti-clockwise", "random", "fixed"]
            for option in options:
                widget.addItem(option)
            widget.setCurrentText(value)
            widget.currentTextChanged.connect(lambda val: self._update_trial(key, val))
        else:
            widget = QLineEdit(value)
            widget.textChanged.connect(lambda val: self._update_trial(key, val))
        return widget

    def _update_trial(self, key: str, value: bool | str | int | float) -> None:
        self.trial[key] = value  # type: ignore

    def get_values(self) -> Trial:
        """Retrieve updated values from the dialog."""
        return self.trial


def get_trial_from_user(
    initial_trial: Trial | None = None,
) -> Trial | None:
    trial = copy.deepcopy(initial_trial) if initial_trial else default_trial()
    dialog = TreeDialog(trial)
    if dialog.exec_() == QDialog.Accepted:
        updated_values = dialog.get_values()
        print("Updated Trial Settings:", updated_values)
    else:
        print("Dialog canceled.")
    return import_and_validate_trial(trial)


def import_and_validate_trial(trial_or_dict: Mapping[str, Any]) -> Trial:
    trial = import_typed_dict(trial_or_dict, default_trial())
    # make any negative time durations zero
    for duration in [
        "condition_timeout",
        "target_duration",
        "central_target_duration",
        "pre_target_delay",
        "pre_central_target_delay",
        "pre_first_target_extra_delay",
        "post_trial_delay",
        "post_block_delay",
    ]:
        if trial[duration] < 0.0:  # type: ignore
            trial[duration] = 0.0  # type: ignore
    # convert string of target indices to a numpy array of ints
    target_indices = np.fromstring(trial["target_indices"], dtype="int", sep=" ")
    if trial["target_order"] == "fixed":
        # clip indices to valid range
        target_indices = np.clip(target_indices, 0, trial["num_targets"] - 1)
    else:
        # construct clockwise sequence
        target_indices = np.array(range(trial["num_targets"]))
        if trial["target_order"] == "anti-clockwise":
            target_indices = np.flip(target_indices)
        elif trial["target_order"] == "random":
            rng = np.random.default_rng()
            rng.shuffle(target_indices)
    # convert array of indices back to a string
    trial["target_indices"] = " ".join(f"{int(i)}" for i in target_indices)
    return trial
