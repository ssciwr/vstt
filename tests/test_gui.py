from __future__ import annotations

import pathlib
from typing import Any
from typing import Tuple

import qt_test_utils as qtu
import vstt
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QInputDialog
from pytest import MonkeyPatch
from vstt.experiment import Experiment
from vstt.gui import Gui


def test_gui_run_no_trials() -> None:
    gui = Gui(filename=None)
    # remove trial conditions
    qtu.press_up_key(gui.trials_widget._widget_list_trials)
    qtu.click(gui.trials_widget._btn_remove)
    # mwt to press escape ok when dialog appears
    mwt = qtu.ModalWidgetTimer(["Enter"])
    mwt.start()
    # try to run experiment
    open_action = gui.toolbar.actions()[4]
    assert open_action.text() == "&Run"
    open_action.trigger()
    assert mwt.widget_type == "QMessageBox"
    assert (
        mwt.widget_text == "Please add a trial condition before running the experiment."
    )


def test_gui_new_file() -> None:
    gui = Gui(filename=None)
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
    gui = Gui(filename=None)
    # initially uses default metadata, display options and trials - no results, no unsaved changes
    assert gui.experiment.metadata == vstt.meta.default_metadata()
    assert gui.experiment.display_options == vstt.display.default_display_options()
    assert gui.experiment.trial_list == [vstt.trial.default_trial()]
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
    tmp_path: pathlib.Path, experiment_with_results: Experiment
) -> None:
    filename = str(tmp_path / "experiment.psydat")
    experiment_with_results.save_psydat(filename)
    gui = Gui(filename=filename)
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


def test_gui_import_excel(
    tmp_path: pathlib.Path, experiment_with_results: Experiment
) -> None:
    filepath = tmp_path / "experiment.xlsx"
    experiment_with_results.save_excel(str(filepath), "trial")
    gui = Gui(filename=str(filepath))
    assert gui.experiment.metadata == experiment_with_results.metadata
    assert gui.experiment.display_options == experiment_with_results.display_options
    assert len(gui.experiment.trial_list) == len(experiment_with_results.trial_list)
    assert gui.experiment.has_unsaved_changes is True
    assert gui.experiment.trial_handler_with_results is None
    assert "*" in gui.windowTitle()
    assert gui.experiment.filename == str(filepath.with_suffix(".psydat"))


def test_gui_import_json(
    tmp_path: pathlib.Path, experiment_with_results: Experiment
) -> None:
    filepath = tmp_path / "experiment.json"
    experiment_with_results.save_json(str(filepath))
    gui = Gui(filename=str(filepath))
    assert gui.experiment.metadata == experiment_with_results.metadata
    assert gui.experiment.display_options == experiment_with_results.display_options
    assert len(gui.experiment.trial_list) == len(experiment_with_results.trial_list)
    assert gui.experiment.has_unsaved_changes is True
    assert gui.experiment.trial_handler_with_results is None
    assert "*" in gui.windowTitle()
    assert gui.experiment.filename == str(filepath.with_suffix(".psydat"))


def test_gui_import_export(
    tmp_path: pathlib.Path,
    experiment_with_results: Experiment,
    monkeypatch: MonkeyPatch,
) -> None:
    filepath = tmp_path / "experiment.psydat"
    experiment_with_results.save_psydat(str(filepath))
    for output_file, filter, data_option in [
        ("t1.xlsx", "Excel file (*.xlsx)", "One page for each trial (default)"),
        ("t2.xlsx", "Excel file (*.xlsx)", "One page for each target"),
        ("t3.json", "JSON file (*.json)", ""),
    ]:
        export_filepath = filepath.parent / output_file
        assert not export_filepath.is_file()

        # monkey patch QFileDialog.getSaveFileName to just return desired filename
        def mock_getSaveFileName(*args: Any, **kwargs: Any) -> Tuple[str, str]:
            return str(export_filepath), filter

        monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_getSaveFileName)

        # monkey patch QInputDialog.getItem to just return desired option
        def mock_getItem(*args: Any, **kwargs: Any) -> Tuple[str, bool]:
            return data_option, True

        monkeypatch.setattr(QInputDialog, "getItem", mock_getItem)

        gui = Gui(filename=str(filepath))
        assert gui.experiment.metadata == experiment_with_results.metadata
        assert gui.experiment.display_options == experiment_with_results.display_options
        assert len(gui.experiment.trial_list) == len(experiment_with_results.trial_list)
        assert gui.experiment.has_unsaved_changes is False
        export_action = gui.toolbar.actions()[3]
        assert export_action.text() == "&Export"
        export_action.trigger()
        assert export_filepath.is_file()
        # re-import exported file
        exp = Experiment(str(export_filepath))
        assert exp.metadata == experiment_with_results.metadata
        assert exp.display_options == experiment_with_results.display_options
        assert exp.trial_list == experiment_with_results.trial_list
        assert exp.trial_handler_with_results is None
        assert exp.has_unsaved_changes is True
        assert exp.filename == str(export_filepath.with_suffix(".psydat"))


def test_gui_invalid_file(tmp_path: pathlib.Path) -> None:
    for extension in ["psydat", "xlsx", "json", "zzz"]:
        file = tmp_path / f"invalid.{extension}"
        file.write_text("beep boop")
        # mwt to click ok when failed to open file message box is shown
        mwt = qtu.ModalWidgetTimer(["Enter"])
        mwt.start()
        gui = Gui(filename=str(file))
        assert mwt.widget_type == "QMessageBox"
        assert "Could not read file" in mwt.widget_text
        assert extension in mwt.widget_text
        gui.close()


def test_gui_nonexistent_file() -> None:
    # mwt to click ok when failed to open file message box is shown
    mwt = qtu.ModalWidgetTimer(["Enter"])
    mwt.start()
    gui = Gui(filename="I dont exist")
    assert mwt.widget_type == "QMessageBox"
    assert "Could not read file" in mwt.widget_text
    gui.close()
