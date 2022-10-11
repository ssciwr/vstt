from __future__ import annotations

import pathlib

import motor_task_prototype.display as mtpdisplay
import motor_task_prototype.meta as mtpmeta
import motor_task_prototype.trial as mtptrial
import qt_test_utils as qtu
from motor_task_prototype.experiment import MotorTaskExperiment
from motor_task_prototype.gui import MotorTaskGui


def test_gui_run_no_trials() -> None:
    gui = MotorTaskGui(filename=None)
    # remove trial conditions
    qtu.press_up_key(gui.trials_widget._widget_list_trials)
    qtu.click(gui.trials_widget._btn_remove)
    # mwt to press escape ok when dialog appears
    mwt = qtu.ModalWidgetTimer(["Enter"])
    mwt.start()
    # try to run experiment
    open_action = gui.toolbar.actions()[3]
    assert open_action.text() == "&Run"
    open_action.trigger()
    assert mwt.widget_type == "QMessageBox"
    assert (
        mwt.widget_text == "Please add a trial condition before running the experiment."
    )


def test_gui_new_file() -> None:
    gui = MotorTaskGui(filename=None)
    # initially uses default metadata, display options and trials - no results, no unsaved changes
    assert gui.experiment.has_unsaved_changes is False
    assert "*" not in gui.windowTitle()
    # make a change so the experiment has unsaved changes
    qtu.click(gui.display_options_widget._widgets["to_target_paths"])
    assert gui.experiment.has_unsaved_changes is True
    assert "*" in gui.windowTitle()
    # new file
    # mwt to press no when save changes dialog appears
    mwt = qtu.ModalWidgetTimer(["N"])
    mwt.start()
    new_action = gui.toolbar.actions()[0]
    assert new_action.text() == "&New"
    new_action.trigger()
    assert mwt.widget_type == "QMessageBox"
    assert mwt.widget_text == "Save your changes before continuing?"
    assert gui.experiment.has_unsaved_changes is False
    assert "*" not in gui.windowTitle()


def test_gui_no_file() -> None:
    gui = MotorTaskGui(filename=None)
    # initially uses default metadata, display options and trials - no results, no unsaved changes
    assert gui.experiment.metadata == mtpmeta.default_metadata()
    assert gui.experiment.display_options == mtpdisplay.default_display_options()
    assert gui.experiment.trial_list == [mtptrial.default_trial()]
    assert gui.experiment.trial_handler_with_results is None
    assert gui.experiment.has_unsaved_changes is False
    assert "*" not in gui.windowTitle()
    # file -> open -> cancel: does nothing
    # mwt to press escape when file open dialog appears
    mwt = qtu.ModalWidgetTimer(["Escape"])
    mwt.start()
    open_action = gui.toolbar.actions()[1]
    assert open_action.text() == "&Open"
    open_action.trigger()
    assert mwt.widget_type == "QFileDialog.Open"
    assert mwt.widget_text == "Open an experiment"
    # make a change so the experiment has unsaved changes
    qtu.click(gui.display_options_widget._widgets["to_target_paths"])
    assert gui.experiment.has_unsaved_changes is True
    assert "*" in gui.windowTitle()
    # mwt to click yes when asked if we want to save our changes
    mwt1 = qtu.ModalWidgetTimer(["Y"])
    # mwt to press escape at subsequent file save dialog
    mwt2 = qtu.ModalWidgetTimer(["Escape"], start_after=mwt1)
    mwt1.start()
    # try to close the gui: yes to save changes but then escape at file save dialog: gui not closed
    gui.close()
    assert mwt1.widget_type == "QMessageBox"
    assert mwt1.widget_text == "Save your changes before continuing?"
    assert mwt2.widget_type == "QFileDialog.Save"
    assert mwt2.widget_text == "Save experiment"
    # mwt to click no when asked if we want to save our changes
    mwt = qtu.ModalWidgetTimer(["N"])
    mwt.start()
    # try close the gui: no to save changes: gui closes
    gui.close()
    assert mwt.widget_type == "QMessageBox"
    assert mwt.widget_text == "Save your changes before continuing?"


def test_gui_file_with_results(
    tmp_path: pathlib.Path, experiment_with_results: MotorTaskExperiment
) -> None:
    filename = str(tmp_path / "experiment.psydat")
    experiment_with_results.save_psydat(filename)
    gui = MotorTaskGui(filename=filename)
    assert gui.experiment.metadata == experiment_with_results.metadata
    assert gui.experiment.display_options == experiment_with_results.display_options
    assert len(gui.experiment.trial_list) == len(experiment_with_results.trial_list)
    assert gui.experiment.has_unsaved_changes is False
    assert gui.experiment.trial_handler_with_results is not None
    assert (
        gui.results_widget._list_trials.count()
        == gui.experiment.trial_handler_with_results.nTotal
    )
    # close the gui: no modal prompt as there are no unsaved changes
    gui.close()


def test_gui_invalid_file(tmp_path: pathlib.Path) -> None:
    file = tmp_path / "invalid.psydat"
    file.write_text("beep boop")
    # mwt to click ok when failed to open file message box is shown
    mwt = qtu.ModalWidgetTimer(["Enter"])
    mwt.start()
    gui = MotorTaskGui(filename=str(file))
    assert mwt.widget_type == "QMessageBox"
    assert "Could not read file" in mwt.widget_text
    gui.close()


def test_gui_nonexistent_file() -> None:
    # mwt to click ok when failed to open file message box is shown
    mwt = qtu.ModalWidgetTimer(["Enter"])
    mwt.start()
    gui = MotorTaskGui(filename="I dont exist")
    assert mwt.widget_type == "QMessageBox"
    assert "Could not read file" in mwt.widget_text
    gui.close()