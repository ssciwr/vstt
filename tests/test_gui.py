import pathlib

import gui_test_utils as gtu
import motor_task_prototype.display as mtpdisplay
import motor_task_prototype.meta as mtpmeta
import motor_task_prototype.trial as mtptrial
from motor_task_prototype.experiment import MotorTaskExperiment
from motor_task_prototype.gui import MotorTaskGui


def test_gui_no_file() -> None:
    gui = MotorTaskGui(filename=None)
    # initially uses default metadata, display options and trials - no results
    assert gui.experiment.metadata == mtpmeta.default_metadata()
    assert gui.experiment.display_options == mtpdisplay.default_display_options()
    assert gui.experiment.trial_list == [mtptrial.default_trial()]
    assert gui.experiment.trial_handler_with_results is None
    assert gui.experiment.has_unsaved_changes is True
    # mwt to click yes when asked if we want to save our changes
    mwt1 = gtu.ModalWidgetTimer(["Y"])
    # mwt to press escape at file save dialog
    mwt2 = gtu.ModalWidgetTimer(["Escape"])
    mwt1.other_mwt_to_start = mwt2
    mwt1.start()
    # try to close the gui: yes to save changes but then escape at file save dialog: gui not closed
    gui.close()
    # mwt to click no when asked if we want to save our changes
    mwt = gtu.ModalWidgetTimer(["N"])
    mwt.start()
    # try close the gui: no to save changes: gui closes
    gui.close()


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
