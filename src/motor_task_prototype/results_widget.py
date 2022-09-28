from collections import defaultdict
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional

from motor_task_prototype.vis import display_results
from psychopy.data import TrialHandlerExt
from PyQt5 import QtWidgets


class ResultsWidget(QtWidgets.QWidget):
    _experiment: Optional[TrialHandlerExt] = None
    _condition_to_trials: DefaultDict[int, List[int]] = defaultdict(list)
    _trial_to_condition: Dict[int, int] = dict()

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        outer_layout = QtWidgets.QVBoxLayout()
        group_box = QtWidgets.QGroupBox("Results")
        outer_layout.addWidget(group_box)
        inner_layout = QtWidgets.QGridLayout()
        group_box.setLayout(inner_layout)
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
        return self.have_results() and 0 <= row < self._list_trials.count()

    def _row_changed(self) -> None:
        valid = self._is_valid(self._list_trials.currentRow())
        self._btn_display_trial.setEnabled(valid)
        self._btn_display_condition.setEnabled(valid)

    def _btn_display_trial_clicked(self) -> None:
        row = self._list_trials.currentRow()
        if not self._is_valid(row):
            return
        display_results(self._experiment, [row])

    def _btn_display_condition_clicked(self) -> None:
        row = self._list_trials.currentRow()
        if not self._is_valid(row):
            return
        condition = self._trial_to_condition[row]
        display_results(self._experiment, self._condition_to_trials[condition])

    def clear_results(self) -> None:
        self._experiment = None
        self._trial_to_condition.clear()
        self._condition_to_trials.clear()
        self._list_trials.clear()

    def have_results(self) -> bool:
        return self._experiment is not None and self._experiment.finished

    def set_results(self, experiment: TrialHandlerExt) -> None:
        self.clear_results()
        self._experiment = experiment
        # assume 1 repetition of experiment
        i_rep = 0
        self._list_trials.clear()
        if experiment.finished is False:
            return
        for trial_index, condition_index in enumerate(experiment.sequenceIndices):
            self._list_trials.addItem(
                f"Trial {trial_index} [Condition {condition_index[i_rep]}]"
            )
            self._condition_to_trials[condition_index[i_rep]].append(trial_index)
            self._trial_to_condition[trial_index] = condition_index[i_rep]
