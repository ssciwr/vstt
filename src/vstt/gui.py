from __future__ import annotations

import logging
import pathlib
from typing import Callable
from typing import Optional

import vstt
from psychopy.visual.window import Window
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from vstt.display_widget import DisplayOptionsWidget
from vstt.experiment import Experiment
from vstt.meta_widget import MetadataWidget
from vstt.results_widget import ResultsWidget
from vstt.task import MotorTask
from vstt.trials_widget import TrialsWidget
from vstt.update import check_for_new_version
from vstt.update import do_pip_upgrade


class Gui(QtWidgets.QMainWindow):
    def __init__(self, filename: Optional[str] = None, win: Optional[Window] = None):
        super().__init__()
        self.experiment = Experiment()
        self._win = win

        grid_layout = QtWidgets.QVBoxLayout()
        split_top_bottom = QtWidgets.QSplitter(Qt.Vertical)

        split_metadata_display = QtWidgets.QSplitter()
        self.metadata_widget = MetadataWidget(self, win=self._win)
        self.metadata_widget.experiment_modified.connect(self.update_window_title)
        split_metadata_display.addWidget(self.metadata_widget)
        self.display_options_widget = DisplayOptionsWidget(self)
        self.display_options_widget.experiment_modified.connect(
            self.update_window_title
        )
        split_metadata_display.addWidget(self.display_options_widget)
        split_metadata_display.setSizes([5000, 1000])

        split_trial_results = QtWidgets.QSplitter()
        self.trials_widget = TrialsWidget(self)
        self.trials_widget.experiment_modified.connect(self.reload_results)
        split_trial_results.addWidget(self.trials_widget)
        self.results_widget = ResultsWidget(self, win=self._win)
        split_trial_results.addWidget(self.results_widget)

        split_top_bottom.addWidget(split_metadata_display)
        split_top_bottom.addWidget(split_trial_results)
        split_top_bottom.setSizes([1000, 5000])
        grid_layout.addWidget(split_top_bottom)

        self.toolbar = _create_menu_and_toolbar(self)
        self.addToolBar(self.toolbar)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(grid_layout)
        self.setCentralWidget(central_widget)
        if filename is not None:
            self._open_file(filename)
        else:
            self.reload_experiment()
        self.resize(800, 600)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.save_changes_check_continue():
            event.accept()
        else:
            event.ignore()

    def btn_new_clicked(self) -> None:
        if self.save_changes_check_continue():
            self.experiment = Experiment()
            self.reload_experiment()

    def _open_file(self, filename: str) -> None:
        try:
            self.experiment.load_file(filename)
        except Exception as e:
            logging.warning(f"Failed to load file {filename}: {e}")
            logging.exception(e)
            QtWidgets.QMessageBox.critical(
                self,
                "Invalid file",
                f"Could not read file '{filename}'",
            )
        self.reload_experiment()

    def btn_open_clicked(self) -> None:
        if self.save_changes_check_continue():
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self,
                "Open an experiment",
                filter="Psydat files (*.psydat) ;; Excel files (*.xlsx) ;; JSON files (*.json) ;; All files (*.*)",
                initialFilter="Psydat files (*.psydat)",
            )
            if filename == "":
                return
            self._open_file(filename)

    def btn_save_clicked(self) -> bool:
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save experiment",
            directory=self.experiment.filename,
            filter="Psydat files (*.psydat)",
        )
        if filename == "":
            return False
        try:
            self.experiment.save_psydat(filename)
        except Exception as e:
            logging.warning(f"Failed to save file {filename}: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "File save error",
                f"Could not save file '{filename}'",
            )
        self.reload_experiment()
        return True

    def btn_export_clicked(self) -> bool:
        filename, selected_filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export experiment",
            directory=str(pathlib.Path(self.experiment.filename).with_suffix(".xlsx")),
            filter="Excel file (*.xlsx) ;; JSON file (*.json)",
            initialFilter="Excel file (*.xlsx)",
        )
        if filename == "":
            return False
        try:
            if selected_filter == "Excel file (*.xlsx)":
                options = [
                    "One page for each trial (default)",
                    "One page for each target",
                ]
                option, ok = QtWidgets.QInputDialog.getItem(
                    self,
                    "Data export options",
                    "Data export option:",
                    options,
                    editable=False,
                )
                if ok is False:
                    return False
                data_format = "target" if "target" in option else "trial"
                self.experiment.save_excel(filename, data_format=data_format)
            elif selected_filter == "JSON file (*.json)":
                self.experiment.save_json(filename)
            else:
                raise RuntimeError(f"Selected filter {selected_filter} is not valid.")
        except Exception as e:
            logging.exception(e)
            QtWidgets.QMessageBox.critical(
                self,
                "File export error",
                f"Could not export file '{filename}'",
            )
        self.reload_experiment()
        return True

    def btn_run_clicked(self) -> None:
        if not self.experiment.trial_list:
            QtWidgets.QMessageBox.warning(
                self,
                "No trial conditions",
                "Please add a trial condition before running the experiment.",
            )
            return
        if self.experiment.trial_handler_with_results is not None:
            yes_no = QtWidgets.QMessageBox.question(
                self,
                "Clear existing results?",
                "Running the experiment will clear the existing results. Continue?",
            )
            if yes_no != QtWidgets.QMessageBox.Yes:
                return
        try:
            task = MotorTask(self.experiment, win=self._win)
            if task.run():
                self.reload_results()
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self,
                "Error running task",
                f"Error running task: {e}",
            )

    def save_changes_check_continue(self) -> bool:
        if self.experiment.has_unsaved_changes:
            yes_no = QtWidgets.QMessageBox.question(
                self,
                "Save changes?",
                "Save your changes before continuing?",
            )
            if yes_no == QtWidgets.QMessageBox.Yes:
                return self.btn_save_clicked()
        return True

    def btn_exit_clicked(self) -> None:
        self.close()

    def reload_results(self) -> None:
        self.results_widget.experiment = self.experiment
        self.update_window_title()

    def update_window_title(self) -> None:
        filename = self.experiment.filename
        if self.experiment.has_unsaved_changes:
            filename += "*"
        self.setWindowTitle(f"{filename} :: VSTT {vstt.__version__}")

    def reload_experiment(self) -> None:
        self.metadata_widget.experiment = self.experiment
        self.display_options_widget.experiment = self.experiment
        self.results_widget.experiment = self.experiment
        self.trials_widget.experiment = self.experiment
        self.update_window_title()

    def about(self) -> None:
        QtWidgets.QMessageBox.about(
            self,
            "About VSTT",
            f"Visuomotor Serial Targeting Task (VSTT)\n\nVersion {vstt.__version__}\n\n"
            + "https://ssciwr.github.io/vstt",
        )

    def check_for_updates(self) -> None:
        title = "Update VSTT"
        QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
        new_version_available, new_version_message = check_for_new_version()
        QtWidgets.QApplication.restoreOverrideCursor()
        if not new_version_available:
            QtWidgets.QMessageBox.information(
                self,
                title,
                new_version_message,
            )
            return
        yes_no = QtWidgets.QMessageBox.question(self, title, new_version_message)
        if yes_no != QtWidgets.QMessageBox.Yes:
            return
        QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
        upgrade_success, upgrade_message = do_pip_upgrade()
        QtWidgets.QApplication.restoreOverrideCursor()
        QtWidgets.QMessageBox.information(self, title, upgrade_message)


def _add_action(
    name: str,
    callback: Callable,
    menu: QtWidgets.QMenu,
    toolbar: Optional[QtWidgets.QToolBar] = None,
    shortcut: Optional[str] = None,
    icon_pixmap: Optional[QtWidgets.QStyle.StandardPixmap] = None,
) -> None:
    action = QtWidgets.QAction(name, menu)
    action.triggered.connect(callback)
    if icon_pixmap is not None:
        action.setIcon(menu.style().standardIcon(icon_pixmap))
    if shortcut is not None:
        action.setShortcut(QtGui.QKeySequence(shortcut))
    menu.addAction(action)
    if toolbar is not None:
        toolbar.addAction(action)


def _create_menu_and_toolbar(gui: vstt.gui.Gui) -> QtWidgets.QToolBar:
    menu = gui.menuBar()
    toolbar = QtWidgets.QToolBar()
    file_menu = menu.addMenu("&File")
    _add_action(
        "&New",
        gui.btn_new_clicked,
        file_menu,
        toolbar,
        "Ctrl+N",
        QtWidgets.QStyle.SP_FileIcon,
    )
    _add_action(
        "&Open",
        gui.btn_open_clicked,
        file_menu,
        toolbar,
        "Ctrl+O",
        QtWidgets.QStyle.SP_DialogOpenButton,
    )
    _add_action(
        "&Save",
        gui.btn_save_clicked,
        file_menu,
        toolbar,
        "Ctrl+S",
        QtWidgets.QStyle.SP_DialogSaveButton,
    )
    _add_action(
        "&Export",
        gui.btn_export_clicked,
        file_menu,
        toolbar,
        None,
        QtWidgets.QStyle.SP_DriveFDIcon,
    )
    _add_action(
        "E&xit",
        gui.btn_exit_clicked,
        file_menu,
        None,
        None,
        QtWidgets.QStyle.SP_DialogCloseButton,
    )
    experiment_menu = menu.addMenu("&Experiment")
    _add_action(
        "&Run",
        gui.btn_run_clicked,
        experiment_menu,
        toolbar,
        "Ctrl+R",
        QtWidgets.QStyle.SP_DialogYesButton,
    )
    help_menu = menu.addMenu("&Help")
    _add_action("&About", gui.about, help_menu)
    _add_action("&Check for updates", gui.check_for_updates, help_menu)
    toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
    return toolbar
