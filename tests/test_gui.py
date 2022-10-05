import pathlib

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


def test_gui_file_with_results(
    tmp_path: pathlib.Path, experiment_with_results: MotorTaskExperiment
) -> None:
    filename = str(tmp_path / "experiment.psydat")
    experiment_with_results.save_psydat(filename)
    gui = MotorTaskGui(filename=filename)
    assert gui.experiment.metadata == experiment_with_results.metadata
    assert gui.experiment.display_options == experiment_with_results.display_options
    assert len(gui.experiment.trial_list) == len(experiment_with_results.trial_list)
    assert gui.experiment.trial_handler_with_results is not None
    assert (
        gui.results_widget._list_trials.count()
        == gui.experiment.trial_handler_with_results.nTotal
    )
