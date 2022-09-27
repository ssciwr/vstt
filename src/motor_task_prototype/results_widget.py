from collections import defaultdict
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional

from motor_task_prototype.vis import display_results
from psychopy.data import TrialHandlerExt
from PyQt5 import QtWidgets


class ResultListWidget(QtWidgets.QWidget):
    experiment: Optional[TrialHandlerExt] = None
    condition_to_trials: DefaultDict[int, List[int]] = defaultdict(list)
    trial_to_condition: Dict[int, int] = dict()

    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        outer_layout = QtWidgets.QVBoxLayout()
        group_box = QtWidgets.QGroupBox("Results")
        outer_layout.addWidget(group_box)
        inner_layout = QtWidgets.QGridLayout()
        group_box.setLayout(inner_layout)
        self.widget_list_trials = QtWidgets.QListWidget()
        self.widget_list_trials.currentRowChanged.connect(self.row_changed)
        self.widget_list_trials.itemDoubleClicked.connect(
            self.btn_display_trial_clicked
        )
        inner_layout.addWidget(self.widget_list_trials, 0, 0, 1, 2)
        self.btn_display_trial = QtWidgets.QPushButton("Display Trial")
        self.btn_display_trial.clicked.connect(self.btn_display_trial_clicked)
        inner_layout.addWidget(self.btn_display_trial, 1, 0)
        self.btn_display_condition = QtWidgets.QPushButton("Display Condition")
        self.btn_display_condition.clicked.connect(self.btn_display_condition_clicked)
        inner_layout.addWidget(self.btn_display_condition, 1, 1)
        self.setLayout(outer_layout)
        self.row_changed()

    def is_valid(self, row: int) -> bool:
        return self.have_results() and 0 <= row < self.widget_list_trials.count()

    def row_changed(self) -> None:
        valid = self.is_valid(self.widget_list_trials.currentRow())
        self.btn_display_trial.setEnabled(valid)
        self.btn_display_condition.setEnabled(valid)

    def btn_display_trial_clicked(self) -> None:
        row = self.widget_list_trials.currentRow()
        if not self.is_valid(row):
            return
        display_results(self.experiment, [row])

    def btn_display_condition_clicked(self) -> None:
        row = self.widget_list_trials.currentRow()
        if not self.is_valid(row):
            return
        condition = self.trial_to_condition[row]
        display_results(self.experiment, self.condition_to_trials[condition])

    def clear_results(self) -> None:
        self.experiment = None
        self.trial_to_condition.clear()
        self.condition_to_trials.clear()
        self.widget_list_trials.clear()

    def have_results(self) -> bool:
        return self.experiment is not None and self.experiment.finished

    def set_results(self, experiment: TrialHandlerExt) -> None:
        self.clear_results()
        self.experiment = experiment
        # assume 1 repetition of experiment
        i_rep = 0
        self.widget_list_trials.clear()
        if experiment.finished is False:
            return
        for trial_index, condition_index in enumerate(experiment.sequenceIndices):
            self.widget_list_trials.addItem(
                f"Trial {trial_index} [Condition {condition_index[i_rep]}]"
            )
            self.condition_to_trials[condition_index[i_rep]].append(trial_index)
            self.trial_to_condition[trial_index] = condition_index[i_rep]
