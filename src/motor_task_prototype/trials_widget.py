from typing import List
from typing import Optional

import PyQt5.QtCore
from motor_task_prototype.trial import describe_trial
from motor_task_prototype.trial import get_trial_from_user
from motor_task_prototype.trial import MotorTaskTrial
from PyQt5 import QtWidgets


class TrialsWidget(QtWidgets.QWidget):
    unsaved_changes: bool = False
    trials_changed = PyQt5.QtCore.pyqtSignal()
    _trial_list: List[MotorTaskTrial] = []
    _confirm_trial_change_with_user = False

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        outer_layout = QtWidgets.QVBoxLayout()
        group_box = QtWidgets.QGroupBox("Trial Conditions")
        outer_layout.addWidget(group_box)
        inner_layout = QtWidgets.QGridLayout()
        group_box.setLayout(inner_layout)
        self._widget_list_trials = QtWidgets.QListWidget()
        self._widget_list_trials.currentRowChanged.connect(self._row_changed)
        self._widget_list_trials.itemDoubleClicked.connect(self._edit_trial)
        inner_layout.addWidget(self._widget_list_trials, 0, 0, 1, 5)
        self._btn_add = QtWidgets.QPushButton("Add")
        self._btn_add.clicked.connect(self._btn_add_clicked)
        inner_layout.addWidget(self._btn_add, 1, 0)
        self._btn_edit = QtWidgets.QPushButton("Edit")
        self._btn_edit.clicked.connect(self._edit_trial)
        inner_layout.addWidget(self._btn_edit, 1, 1)
        self._btn_move_up = QtWidgets.QPushButton("Move Up")
        self._btn_move_up.clicked.connect(self._btn_move_up_clicked)
        inner_layout.addWidget(self._btn_move_up, 1, 2)
        self._btn_move_down = QtWidgets.QPushButton("Move Down")
        self._btn_move_down.clicked.connect(self._btn_move_down_clicked)
        inner_layout.addWidget(self._btn_move_down, 1, 3)
        self._btn_remove = QtWidgets.QPushButton("Remove")
        self._btn_remove.clicked.connect(self._btn_remove_clicked)
        inner_layout.addWidget(self._btn_remove, 1, 4)
        self.setLayout(outer_layout)
        self._row_changed()
        self.unsaved_changes = False

    def _is_valid(self, row: int) -> bool:
        return 0 <= row < len(self._trial_list)

    def _can_move_up(self, row: int) -> bool:
        return 1 <= row < len(self._trial_list)

    def _can_move_down(self, row: int) -> bool:
        return 0 <= row < len(self._trial_list) - 1

    def _row_changed(self) -> None:
        row = self._widget_list_trials.currentRow()
        self._btn_edit.setEnabled(self._is_valid(row))
        self._btn_remove.setEnabled(self._is_valid(row))
        self._btn_move_up.setEnabled(self._can_move_up(row))
        self._btn_move_down.setEnabled(self._can_move_down(row))

    def _current_trial(self) -> Optional[MotorTaskTrial]:
        row = self._widget_list_trials.currentRow()
        if not self._is_valid(row):
            return None
        return self._trial_list[row]

    def _confirm_clear_data(self) -> bool:
        if not self._confirm_trial_change_with_user:
            self.unsaved_changes = True
            return True
        yes_no = QtWidgets.QMessageBox.question(
            self,
            "Clear existing results?",
            "Modifying the trial conditions will clear the existing results. Continue?",
        )
        if yes_no == QtWidgets.QMessageBox.Yes:
            self._confirm_trial_change_with_user = False
            self.unsaved_changes = True
            self.trials_changed.emit()
            return True
        return False

    def _btn_add_clicked(self) -> None:
        if not self._confirm_clear_data():
            return
        trial = get_trial_from_user(self._current_trial())
        if trial is not None:
            self._trial_list.append(trial)
            self._widget_list_trials.addItem(describe_trial(trial))
            self._widget_list_trials.setCurrentRow(len(self._trial_list) - 1)

    def _swap_rows(self, row1: int, row2: int) -> None:
        if not self._is_valid(row1) or not self._is_valid(row2):
            return
        if not self._confirm_clear_data():
            return
        self._trial_list[row1], self._trial_list[row2] = (
            self._trial_list[row2],
            self._trial_list[row1],
        )
        self._widget_list_trials.insertItem(
            row2, self._widget_list_trials.takeItem(row1)
        )
        self._widget_list_trials.setCurrentRow(row2)

    def _btn_move_up_clicked(self) -> None:
        row = self._widget_list_trials.currentRow()
        self._swap_rows(row, row - 1)

    def _btn_move_down_clicked(self) -> None:
        row = self._widget_list_trials.currentRow()
        self._swap_rows(row, row + 1)

    def _btn_remove_clicked(self) -> None:
        row = self._widget_list_trials.currentRow()
        if not self._is_valid(row):
            return
        if not self._confirm_clear_data():
            return
        self._trial_list.pop(row)
        self._widget_list_trials.takeItem(row)
        self._row_changed()

    def _edit_trial(self) -> None:
        row = self._widget_list_trials.currentRow()
        if not self._is_valid(row):
            return
        if not self._confirm_clear_data():
            return
        edited_trial = get_trial_from_user(self._trial_list[row])
        if edited_trial is not None:
            self._trial_list[row] = edited_trial
            item = self._widget_list_trials.item(row)
            assert item is not None
            item.setText(describe_trial(edited_trial))

    def set_trial_list(
        self, trial_list: List[MotorTaskTrial], confirm_trial_change_with_user: bool
    ) -> None:
        self._trial_list = trial_list
        self._widget_list_trials.clear()
        self._widget_list_trials.addItems(
            [describe_trial(trial) for trial in trial_list]
        )
        self._confirm_trial_change_with_user = confirm_trial_change_with_user
        self.unsaved_changes = False

    def get_trial_list(self) -> List[MotorTaskTrial]:
        return self._trial_list
