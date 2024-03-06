from __future__ import annotations

import logging
import pathlib

import numpy as np
from psychopy.visual.window import Window
from qtpy import QtWidgets
from qtpy.compat import getsavefilename

from vstt.experiment import Experiment
from vstt.vis import display_results


class ResultsWidget(QtWidgets.QWidget):
    def __init__(
        self, parent: QtWidgets.QWidget | None = None, win: Window | None = None
    ):
        super().__init__(parent)
        self._win = win
        self._experiment = Experiment()

        outer_layout = QtWidgets.QVBoxLayout()
        group_box = QtWidgets.QGroupBox("Results")
        outer_layout.addWidget(group_box)
        inner_layout = QtWidgets.QGridLayout()
        group_box.setLayout(inner_layout)
        self._list_trial_row_to_trial_index: list[int] = []
        self._list_trials = QtWidgets.QListWidget()
        self._list_trials.currentRowChanged.connect(self._row_changed)
        self._list_trials.itemDoubleClicked.connect(self._btn_display_trial_clicked)
        inner_layout.addWidget(self._list_trials, 0, 0, 1, 4)
        self._btn_display_trial = QtWidgets.QPushButton("View Trial")
        self._btn_display_trial.clicked.connect(self._btn_display_trial_clicked)
        inner_layout.addWidget(self._btn_display_trial, 1, 0)
        self._btn_screenshot_trial = QtWidgets.QPushButton("Trial Image")
        self._btn_screenshot_trial.clicked.connect(self._btn_screenshot_trial_clicked)
        inner_layout.addWidget(self._btn_screenshot_trial, 1, 1)
        self._btn_display_condition = QtWidgets.QPushButton("View Condition")
        self._btn_display_condition.clicked.connect(self._btn_display_condition_clicked)
        inner_layout.addWidget(self._btn_display_condition, 1, 2)
        self._btn_screenshot_condition = QtWidgets.QPushButton("Condition Image")
        self._btn_screenshot_condition.clicked.connect(
            self._btn_screenshot_condition_clicked
        )
        inner_layout.addWidget(self._btn_screenshot_condition, 1, 3)
        self.setLayout(outer_layout)
        self._row_changed()

    def _is_valid(self, row: int) -> bool:
        if (
            self._list_trials.count() > 0
            and self.experiment.trial_handler_with_results is None
        ):
            # experiment results have been cleared - re-assign experiment to update widget
            self.experiment = self._experiment
            return False
        return (
            self.experiment.trial_handler_with_results is not None
            and 0 <= row < self._list_trials.count()
        )

    def _row_changed(self) -> None:
        valid = self._is_valid(self._list_trials.currentRow())
        self._btn_display_trial.setEnabled(valid)
        self._btn_screenshot_trial.setEnabled(valid)
        self._btn_display_condition.setEnabled(valid)
        self._btn_screenshot_condition.setEnabled(valid)

    def _display_results(
        self, all_trials_for_this_condition: bool, screenshot: bool
    ) -> None:
        row = self._list_trials.currentRow()
        if not self._is_valid(row):
            return
        screenshot_image = display_results(
            60,
            True,
            False,
            self._experiment.trial_handler_with_results,
            self._experiment.display_options,
            self._list_trial_row_to_trial_index[row],
            all_trials_for_this_condition,
            win=self._win,
            return_screenshot=screenshot,
        )
        if screenshot:
            if screenshot_image is None:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Screenshot error",
                    "Could not take screenshot",
                )
                return
            filename, _ = getsavefilename(
                self,
                "Save screenshot",
                "screenshot.png",
                "Png image file (*.png)",
            )
            if filename == "":
                return
            try:
                screenshot_image.save(pathlib.Path(filename).with_suffix(".png"))
            except Exception as e:
                logging.warning(f"Failed to save file {filename}: {e}")
                QtWidgets.QMessageBox.critical(
                    self,
                    "File save error",
                    f"Could not save file '{filename}'",
                )

    def _btn_display_trial_clicked(self) -> None:
        self._display_results(False, False)

    def _btn_screenshot_trial_clicked(self) -> None:
        self._display_results(False, True)

    def _btn_display_condition_clicked(self) -> None:
        self._display_results(True, False)

    def _btn_screenshot_condition_clicked(self) -> None:
        self._display_results(True, True)

    @property
    def experiment(self) -> Experiment:
        return self._experiment

    @experiment.setter
    def experiment(self, experiment: Experiment) -> None:
        self._list_trials.clear()
        self._list_trial_row_to_trial_index.clear()
        self._experiment = experiment
        trial_handler = experiment.trial_handler_with_results
        if trial_handler is None:
            return
        # assume 1 repetition of experiment
        rep_index = 0
        for trial_index, condition_index in enumerate(trial_handler.sequenceIndices):
            # trials that have no data have a default string instead of a numpy array
            if (
                type(trial_handler.data["target_indices"][(trial_index, rep_index)])
                is np.ndarray
            ):
                self._list_trials.addItem(
                    f"Trial {trial_index} [Condition {condition_index[rep_index]}]"
                )
                self._list_trial_row_to_trial_index.append(trial_index)
