from typing import Callable
from typing import Optional

import motor_task_prototype as mtp
from motor_task_prototype.display_widget import DisplayOptionsWidget
from motor_task_prototype.experiment import get_experiment_filename_from_user
from motor_task_prototype.experiment import import_experiment_from_file
from motor_task_prototype.experiment import new_default_experiment
from motor_task_prototype.experiment import save_experiment
from motor_task_prototype.meta_widget import MetadataWidget
from motor_task_prototype.results_widget import ResultsWidget
from motor_task_prototype.task import run_task
from motor_task_prototype.trials_widget import TrialsWidget
from psychopy.data import TrialHandlerExt
from psychopy.visual.window import Window
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt


class MotorTaskGui(QtWidgets.QMainWindow):
    experiment: TrialHandlerExt
    unsaved_changes: bool = False
    _win: Optional[Window]
    _win_type: str

    def __init__(
        self,
        filename: Optional[str] = None,
        win: Optional[Window] = None,
        win_type: str = "pyglet",
    ):
        super().__init__()
        self._win = win
        self._win_type = win_type
        if filename:
            self.experiment = import_experiment_from_file(
                filename
            )  # todo: handle failure here gracefully
        else:
            self.experiment = new_default_experiment()
        self.setWindowTitle(f"Motor Task Prototype {mtp.__version__}")

        grid_layout = QtWidgets.QVBoxLayout()
        split_top_bottom = QtWidgets.QSplitter(Qt.Vertical)

        split_metadata_display = QtWidgets.QSplitter()
        self.metadata_widget = MetadataWidget(
            self, win=self._win, win_type=self._win_type
        )
        split_metadata_display.addWidget(self.metadata_widget)

        self.display_options_widget = DisplayOptionsWidget(self)
        split_metadata_display.addWidget(self.display_options_widget)
        split_metadata_display.setSizes([5000, 1000])

        split_trial_results = QtWidgets.QSplitter()
        self.trials_widget = TrialsWidget(self)
        split_trial_results.addWidget(self.trials_widget)
        self.results_widget = ResultsWidget(
            self, win=self._win, win_type=self._win_type
        )
        split_trial_results.addWidget(self.results_widget)

        self.trials_widget.trials_changed.connect(self.results_widget.clear_results)

        split_top_bottom.addWidget(split_metadata_display)
        split_top_bottom.addWidget(split_trial_results)
        split_top_bottom.setSizes([1000, 5000])
        grid_layout.addWidget(split_top_bottom)

        create_menu_and_toolbar(self)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(grid_layout)
        self.setCentralWidget(central_widget)
        self.reload_experiment()
        self.resize(800, 600)

    def btn_new_clicked(self) -> None:
        if self.save_changes_check_continue():
            self.experiment = new_default_experiment()
            self.reload_experiment()

    def btn_open_clicked(self) -> None:
        if self.save_changes_check_continue():
            filename = get_experiment_filename_from_user()
            if filename is not None:
                self.experiment = import_experiment_from_file(filename)
                self.reload_experiment()

    def btn_save_clicked(self) -> bool:
        success = save_experiment(self.experiment)
        if success:
            self.reload_experiment()
        return success

    def btn_run_clicked(self) -> None:
        if not self.trials_widget.get_trial_list():
            QtWidgets.QMessageBox.warning(
                self,
                "No trial conditions",
                "Please add a trial condition before running the experiment.",
            )
            return
        if self.results_widget.have_results():
            yes_no = QtWidgets.QMessageBox.question(
                self,
                "Clear existing results?",
                "Running the experiment will clear the existing results. Continue?",
            )
            if yes_no != QtWidgets.QMessageBox.Yes:
                return
        experiment_with_results = run_task(
            self.experiment, win=self._win, win_type=self._win_type
        )
        if experiment_with_results is not None:
            self.experiment = experiment_with_results
            self.reload_experiment()
            self.unsaved_changes = True

    def save_changes_check_continue(self) -> bool:
        if (
            self.unsaved_changes
            or self.metadata_widget.unsaved_changes
            or self.display_options_widget.unsaved_changes
            or self.trials_widget.unsaved_changes
        ):
            yes_no = QtWidgets.QMessageBox.question(
                self,
                "Save changes?",
                "Save your changes to a file before continuing?",
            )
            if yes_no == QtWidgets.QMessageBox.Yes:
                return self.btn_save_clicked()
        return True

    def btn_exit_clicked(self) -> None:
        if self.save_changes_check_continue():
            self.close()

    def reload_experiment(self) -> None:
        self.metadata_widget.set_metadata(self.experiment.extraInfo["metadata"])
        self.display_options_widget.set_display_options(
            self.experiment.extraInfo["display_options"]
        )
        self.results_widget.set_results(self.experiment)
        self.trials_widget.set_trial_list(
            self.experiment.trialList, self.results_widget.have_results()
        )
        self.unsaved_changes = False

    def about(self) -> None:
        QtWidgets.QMessageBox.about(
            self,
            "About Motor Task Prototype",
            f"Motor Task Prototype {mtp.__version__}\n\n"
            f"Psychopy backend: {self._win_type}\n\n"
            + "https://ssciwr.github.io/motor-task-prototype",
        )


def add_action(
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


def create_menu_and_toolbar(gui: MotorTaskGui) -> None:
    menu = gui.menuBar()
    toolbar = QtWidgets.QToolBar()
    file_menu = menu.addMenu("&File")
    add_action(
        "&New",
        gui.btn_new_clicked,
        file_menu,
        toolbar,
        "Ctrl+N",
        QtWidgets.QStyle.SP_FileIcon,
    )
    add_action(
        "&Open",
        gui.btn_open_clicked,
        file_menu,
        toolbar,
        "Ctrl+O",
        QtWidgets.QStyle.SP_DialogOpenButton,
    )
    add_action(
        "&Save",
        gui.btn_save_clicked,
        file_menu,
        toolbar,
        "Ctrl+S",
        QtWidgets.QStyle.SP_DialogSaveButton,
    )
    add_action(
        "E&xit",
        gui.btn_exit_clicked,
        file_menu,
        None,
        "Ctrl+X",
        QtWidgets.QStyle.SP_DialogCloseButton,
    )
    experiment_menu = menu.addMenu("&Experiment")
    add_action(
        "&Run",
        gui.btn_run_clicked,
        experiment_menu,
        toolbar,
        "Ctrl+R",
        QtWidgets.QStyle.SP_DialogYesButton,
    )
    help_menu = menu.addMenu("&Help")
    add_action("&About", gui.about, help_menu)
    toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
    gui.addToolBar(toolbar)
