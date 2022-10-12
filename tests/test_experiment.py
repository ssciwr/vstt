from __future__ import annotations

import pathlib
import pickle

import numpy as np
import pytest
from motor_task_prototype.display import default_display_options
from motor_task_prototype.experiment import MotorTaskExperiment
from motor_task_prototype.meta import default_metadata
from motor_task_prototype.trial import default_trial
from psychopy.data import TrialHandlerExt


def test_experiment_no_results(tmp_path: pathlib.Path) -> None:
    exp = MotorTaskExperiment()
    # default initial values
    assert exp.trial_list == [default_trial()]
    assert exp.metadata == default_metadata()
    assert exp.display_options == default_display_options()
    assert exp.trial_handler_with_results is None
    assert exp.has_unsaved_changes is False
    # get a trial handler for this experiment
    th = exp.create_trialhandler()
    assert th.trialList == [default_trial()]
    assert th.extraInfo["metadata"] == default_metadata()
    assert th.extraInfo["display_options"] == default_display_options()
    assert th.finished is False
    # modify experiment
    exp.trial_list.append(default_trial())
    exp.metadata["author"] = "Joe Smith"
    exp.display_options["to_target_paths"] = False
    assert exp.trial_handler_with_results is None
    # get a new trial handler
    th = exp.create_trialhandler()
    assert th.trialList == [default_trial(), default_trial()]
    assert th.extraInfo["metadata"]["author"] == "Joe Smith"
    assert th.extraInfo["display_options"]["to_target_paths"] is False
    assert th.finished is False
    # save the experiment (psydat file extension is automatically added if missing)
    filename_to_save = str(tmp_path / "ex1")
    filename_to_load = str(tmp_path / "ex1.psydat")
    exp.save_psydat(filename_to_save)
    assert exp.has_unsaved_changes is False
    # load the experiment
    exp2 = MotorTaskExperiment(filename_to_load)
    assert exp2.metadata["author"] == "Joe Smith"
    assert exp2.display_options["to_target_paths"] is False
    assert exp2.has_unsaved_changes is False
    assert exp.trial_handler_with_results is None
    # get a new trial handler
    th2 = exp2.create_trialhandler()
    assert th2.trialList == [default_trial(), default_trial()]
    assert th2.extraInfo["metadata"]["author"] == "Joe Smith"
    assert th2.extraInfo["display_options"]["to_target_paths"] is False
    assert th2.finished is False


def test_experiment_with_results(
    experiment_with_results: MotorTaskExperiment, tmp_path: pathlib.Path
) -> None:
    # initial experiment has existing results
    assert experiment_with_results.trial_handler_with_results is not None
    assert experiment_with_results.trial_handler_with_results.finished
    assert (
        "to_target_timestamps"
        in experiment_with_results.trial_handler_with_results.data
    )
    assert experiment_with_results.has_unsaved_changes is True
    # get a new trial handler for this experiment
    th = experiment_with_results.create_trialhandler()
    assert th.trialList == experiment_with_results.trial_list
    assert th.extraInfo["metadata"] == experiment_with_results.metadata
    assert th.extraInfo["display_options"] == experiment_with_results.display_options
    assert "to_target_timestamps" not in th.data
    assert th.finished is False
    # save experiment
    filename = str(tmp_path / "ex1.psydat")
    experiment_with_results.save_psydat(filename)
    assert experiment_with_results.has_unsaved_changes is False
    # load the experiment
    exp2 = MotorTaskExperiment(filename)
    assert exp2.metadata == experiment_with_results.metadata
    assert exp2.display_options == experiment_with_results.display_options
    assert exp2.trial_list == experiment_with_results.trial_list
    assert exp2.has_unsaved_changes is False
    assert exp2.trial_handler_with_results is not None
    for key in [
        "target_pos",
        "to_target_timestamps",
        "to_center_timestamps",
        "to_target_mouse_positions",
        "to_center_mouse_positions",
    ]:
        for trial1, trial2 in zip(
            exp2.trial_handler_with_results.data[key],
            experiment_with_results.trial_handler_with_results.data[key],
        ):
            for rep1, rep2 in zip(trial1, trial2):
                for data1, data2 in zip(rep1, rep2):
                    assert np.allclose(data1, data2)
    # get a new trial handler
    th2 = exp2.create_trialhandler()
    assert th2.trialList == experiment_with_results.trial_list
    assert th2.extraInfo["metadata"] == experiment_with_results.metadata
    assert th2.extraInfo["display_options"] == experiment_with_results.display_options
    assert "to_target_timestamps" not in th2.data
    assert th2.finished is False


def test_experiment_to_excel(
    experiment_with_results: MotorTaskExperiment, tmp_path: pathlib.Path
) -> None:
    # export to an Excel file
    excel_file = tmp_path / "export.xlsx"
    experiment_with_results.save_excel(str(excel_file))
    # import this Excel file again
    exp = MotorTaskExperiment(str(excel_file))
    assert exp.metadata == experiment_with_results.metadata
    assert exp.display_options == experiment_with_results.display_options
    assert exp.trial_list == experiment_with_results.trial_list
    assert exp.trial_handler_with_results is None
    assert exp.has_unsaved_changes is True
    assert exp.filename == str(excel_file.with_suffix(".psydat"))


def test_experiment_to_json(
    experiment_with_results: MotorTaskExperiment, tmp_path: pathlib.Path
) -> None:
    # export to a json file
    json_file = tmp_path / "export.json"
    experiment_with_results.save_json(str(json_file))
    # import this json file again
    exp = MotorTaskExperiment(str(json_file))
    assert exp.metadata == experiment_with_results.metadata
    assert exp.display_options == experiment_with_results.display_options
    assert exp.trial_list == experiment_with_results.trial_list
    assert exp.trial_handler_with_results is None
    assert exp.has_unsaved_changes is True
    assert exp.filename == str(json_file.with_suffix(".psydat"))


def test_experiment_invalid_file(tmp_path: pathlib.Path) -> None:
    # file doesn't exist
    with pytest.raises(ValueError):
        MotorTaskExperiment("I don't exist!")

    # file exists and has psydat extension but is garbage
    file = tmp_path / "invalid.psydat"
    file.write_text("beep boop")
    with pytest.raises(pickle.PickleError):
        MotorTaskExperiment(str(file))


def test_experiment_empty_trialhandler() -> None:
    # construct an empty TrialHandlerExt: no trials, no extraInfo dict
    empty_th = TrialHandlerExt([], 1)
    # this is what gets constructed from an empty trial list:
    assert empty_th.trialList == [None]
    assert empty_th.extraInfo is None
    experiment = MotorTaskExperiment()
    experiment.import_and_validate_trial_handler(empty_th)
    # defaults are used for missing metadata and display_options
    assert experiment.metadata == default_metadata()
    assert experiment.display_options == default_display_options()
    assert len(experiment.trial_list) == 0
