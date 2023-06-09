from __future__ import annotations

from typing import List
from typing import Optional

import numpy as np
from psychopy.visual.window import Window
from PyQt5 import QtWidgets
from vstt.experiment import Experiment
from vstt.vis import display_results


class ResultsWidget(QtWidgets.QWidget):
    def __init__(
        self, parent: Optional[QtWidgets.QWidget] = None, win: Optional[Window] = None
    ):
        super().__init__(parent)
        self._win = win
        self._experiment = Experiment()

        outer_layout = QtWidgets.QVBoxLayout()
        group_box = QtWidgets.QGroupBox("Results")
        outer_layout.addWidget(group_box)
        inner_layout = QtWidgets.QGridLayout()
        group_box.setLayout(inner_layout)
        self._list_trial_row_to_trial_index: List[int] = []
        self._list_trials = QtWidgets.QListWidget()
        self._list_trials.currentRowChanged.connect(self._row_changed)
        self._list_trials.itemDoubleClicked.connect(self._btn_display_trial_clicked)
        inner_layout.addWidget(self._list_trials, 0, 0, 1, 2)
        self._btn_display_trial = QtWidgets.QPushButton("Display Trial")
        self._btn_display_trial.clicked.connect(self._btn_display_trial_clicked)
        inner_layout.addWidget(self._btn_display_trial, 1, 0)
        self._btn_display_condition = QtWidgets.QPushButton("Display Condition")
        self._btn_display_condition.clicked.connect(self._btn_display_condition_clicked)
        inner_layout.addWidget(self._btn_display_condition, 1, 1)
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
        self._btn_display_condition.setEnabled(valid)

    def _display_results(self, all_trials_for_this_condition: bool) -> None:
        row = self._list_trials.currentRow()
        if not self._is_valid(row):
            return
        display_results(
            60,
            True,
            False,
            self._experiment.trial_handler_with_results,
            self._experiment.display_options,
            self._list_trial_row_to_trial_index[row],
            all_trials_for_this_condition,
            win=self._win,
        )

    def _btn_display_trial_clicked(self) -> None:
        self._display_results(False)

    def _btn_display_condition_clicked(self) -> None:
        self._display_results(True)

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
