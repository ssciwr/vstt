import pathlib

import motor_task_prototype.display as mtpdisplay
import motor_task_prototype.meta as mtpmeta
import motor_task_prototype.trial as mtptrial
from motor_task_prototype.gui import MotorTaskGui
from psychopy.data import TrialHandlerExt


def test_gui_no_file() -> None:
    gui = MotorTaskGui(filename=None)
    # initially uses default metadata, display options and trials - no results
    assert gui.metadata_widget.get_metadata() == mtpmeta.default_metadata()
    assert (
        gui.display_options_widget.get_display_options()
        == mtpdisplay.default_display_options()
    )
    assert gui.trials_widget.get_trial_list() == [mtptrial.default_trial()]
    assert gui.results_widget.have_results() is False


def test_gui_file_with_results(
    tmp_path: pathlib.Path, experiment_with_results: TrialHandlerExt
) -> None:
    filename = str(tmp_path / "experiment.psydat")
    experiment_with_results.saveAsPickle(filename)
    gui = MotorTaskGui(filename=filename)
    assert (
        gui.metadata_widget.get_metadata()
        == experiment_with_results.extraInfo["metadata"]
    )
    assert (
        gui.display_options_widget.get_display_options()
        == experiment_with_results.extraInfo["display_options"]
    )
    assert len(gui.trials_widget.get_trial_list()) == len(
        experiment_with_results.trialList
    )
    assert gui.results_widget.have_results() is True
    assert gui.results_widget._list_trials.count() == experiment_with_results.nTotal
