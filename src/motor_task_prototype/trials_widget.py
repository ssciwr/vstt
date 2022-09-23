from typing import List
from typing import Optional

import PyQt5.QtCore
from motor_task_prototype.trial import describe_trial
from motor_task_prototype.trial import get_trial_from_user
from motor_task_prototype.trial import MotorTaskTrial
from PyQt5 import QtWidgets


class TrialListWidget(QtWidgets.QWidget):
    trial_list: List[MotorTaskTrial] = []
    trials_changed = PyQt5.QtCore.pyqtSignal()
    unsaved_changes: bool = False
    have_data = False

    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        outer_layout = QtWidgets.QVBoxLayout()
        group_box = QtWidgets.QGroupBox("Trial Conditions")
        outer_layout.addWidget(group_box)
        inner_layout = QtWidgets.QGridLayout()
        group_box.setLayout(inner_layout)
        self.widget_list_trials = QtWidgets.QListWidget()
        self.widget_list_trials.currentRowChanged.connect(self.row_changed)
        self.widget_list_trials.itemDoubleClicked.connect(self.edit_trial)
        inner_layout.addWidget(self.widget_list_trials, 0, 0, 1, 5)
        self.btn_add = QtWidgets.QPushButton("Add")
        self.btn_add.clicked.connect(self.btn_add_clicked)
        inner_layout.addWidget(self.btn_add, 1, 0)
        self.btn_edit = QtWidgets.QPushButton("Edit")
        self.btn_edit.clicked.connect(self.edit_trial)
        inner_layout.addWidget(self.btn_edit, 1, 1)
        self.btn_move_up = QtWidgets.QPushButton("Move Up")
        self.btn_move_up.clicked.connect(self.btn_move_up_clicked)
        inner_layout.addWidget(self.btn_move_up, 1, 2)
        self.btn_move_down = QtWidgets.QPushButton("Move Down")
        self.btn_move_down.clicked.connect(self.btn_move_down_clicked)
        inner_layout.addWidget(self.btn_move_down, 1, 3)
        self.btn_remove = QtWidgets.QPushButton("Remove")
        self.btn_remove.clicked.connect(self.btn_remove_clicked)
        inner_layout.addWidget(self.btn_remove, 1, 4)
        self.setLayout(outer_layout)
        self.row_changed()
        self.unsaved_changes = False

    def is_valid(self, row: int) -> bool:
        return 0 <= row < len(self.trial_list)

    def can_move_up(self, row: int) -> bool:
        return 1 <= row < len(self.trial_list)

    def can_move_down(self, row: int) -> bool:
        return 0 <= row < len(self.trial_list) - 1

    def row_changed(self) -> None:
        row = self.widget_list_trials.currentRow()
        self.btn_edit.setEnabled(self.is_valid(row))
        self.btn_remove.setEnabled(self.is_valid(row))
        self.btn_move_up.setEnabled(self.can_move_up(row))
        self.btn_move_down.setEnabled(self.can_move_down(row))

    def current_trial(self) -> Optional[MotorTaskTrial]:
        row = self.widget_list_trials.currentRow()
        if not self.is_valid(row):
            return None
        return self.trial_list[row]

    def confirm_clear_data(self) -> bool:
        if not self.have_data:
            self.unsaved_changes = True
            return True
        yes_no = QtWidgets.QMessageBox.question(
            self,
            "Clear existing results?",
            "Modifying the trial conditions will clear the existing results. Continue?",
        )
        if yes_no == QtWidgets.QMessageBox.Yes:
            self.have_data = False
            self.unsaved_changes = True
            self.trials_changed.emit()
            return True
        return False

    def btn_add_clicked(self) -> None:
        if not self.confirm_clear_data():
            return
        trial = get_trial_from_user(self.current_trial())
        if trial is not None:
            self.trial_list.append(trial)
            self.widget_list_trials.addItem(describe_trial(trial))
            self.widget_list_trials.setCurrentRow(len(self.trial_list) - 1)

    def swap_rows(self, row1: int, row2: int) -> None:
        if not self.is_valid(row1) or not self.is_valid(row2):
            return
        if not self.confirm_clear_data():
            return
        self.trial_list[row1], self.trial_list[row2] = (
            self.trial_list[row2],
            self.trial_list[row1],
        )
        self.widget_list_trials.insertItem(row2, self.widget_list_trials.takeItem(row1))
        self.widget_list_trials.setCurrentRow(row2)

    def btn_move_up_clicked(self) -> None:
        row = self.widget_list_trials.currentRow()
        self.swap_rows(row, row - 1)

    def btn_move_down_clicked(self) -> None:
        row = self.widget_list_trials.currentRow()
        self.swap_rows(row, row + 1)

    def btn_remove_clicked(self) -> None:
        row = self.widget_list_trials.currentRow()
        if not self.is_valid(row):
            return
        if not self.confirm_clear_data():
            return
        self.trial_list.pop(row)
        self.widget_list_trials.takeItem(row)
        self.row_changed()

    def edit_trial(self) -> None:
        row = self.widget_list_trials.currentRow()
        if not self.is_valid(row):
            return
        if not self.confirm_clear_data():
            return
        edited_trial = get_trial_from_user(self.trial_list[row])
        if edited_trial is not None:
            self.trial_list[row] = edited_trial
            item = self.widget_list_trials.item(row)
            assert item is not None
            item.setText(describe_trial(edited_trial))

    def set_trial_list(self, trial_list: List[MotorTaskTrial], have_data: bool) -> None:
        self.trial_list = trial_list
        self.widget_list_trials.clear()
        self.widget_list_trials.addItems(
            [describe_trial(trial) for trial in trial_list]
        )
        self.have_data = have_data
        self.unsaved_changes = False

    def get_trial_list(self) -> List[MotorTaskTrial]:
        return self.trial_list
