from __future__ import annotations

import pathlib
import pickle

import numpy as np
import pandas as pd
import pytest
from psychopy.data import TrialHandlerExt
from vstt.display import default_display_options
from vstt.experiment import Experiment
from vstt.meta import default_metadata
from vstt.trial import default_trial


def test_experiment_no_results(tmp_path: pathlib.Path) -> None:
    exp = Experiment()
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
    exp2 = Experiment(filename_to_load)
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
    experiment_with_results: Experiment, tmp_path: pathlib.Path
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
    exp2 = Experiment(filename)
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


def test_experiment_to_excel_target_data_format(
    experiment_with_results: Experiment, tmp_path: pathlib.Path
) -> None:
    # export to an Excel file with a sheet for each target
    excel_file = tmp_path / "export.xlsx"
    experiment_with_results.save_excel(str(excel_file), data_format="target")
    stats: pd.DataFrame = experiment_with_results.stats
    # import this Excel file again
    exp = Experiment(str(excel_file))
    assert exp.metadata == experiment_with_results.metadata
    assert exp.display_options == experiment_with_results.display_options
    assert exp.trial_list == experiment_with_results.trial_list
    assert exp.trial_handler_with_results is None
    assert exp.has_unsaved_changes is True
    assert exp.filename == str(excel_file.with_suffix(".psydat"))
    # check that results sheets in Excel are consistent with stats dataframe
    dfs = pd.read_excel(excel_file, sheet_name=None)
    df_stats = dfs["statistics"]
    # convert x,y columns back to single (x,y) tuple column
    df_stats["center_pos"] = list(zip(df_stats.center_pos_x, df_stats.center_pos_y))
    df_stats.drop(columns=["center_pos_x", "center_pos_y"], inplace=True)
    df_stats["target_pos"] = list(zip(df_stats.target_pos_x, df_stats.target_pos_y))
    df_stats.drop(columns=["target_pos_x", "target_pos_y"], inplace=True)
    for name in df_stats:
        for a, b in zip(stats[name], df_stats[name]):
            assert np.allclose(a, b, equal_nan=True)
    assert len(dfs) == 4 + sum(
        [
            trial["weight"] * trial["num_targets"]
            for trial in experiment_with_results.trial_list
        ]
    )
    # check that excel sheet for each target is consistent with corresponding stats dataframe row
    for i_row in range(stats.shape[0]):
        df_data = dfs[f"{i_row}"]
        for label in ["to_target_timestamps", "to_center_timestamps"]:
            correct_values = stats[label][i_row]
            n = correct_values.shape[0]
            assert np.allclose(df_data[label].to_numpy()[0:n], correct_values)
        for label in ["to_target_mouse_positions", "to_center_mouse_positions"]:
            correct_values = stats[label][i_row]
            n = correct_values.shape[0]
            if n > 0:
                assert np.allclose(
                    df_data[f"{label}_x"].to_numpy()[0:n], correct_values[:, 0]
                )
                assert np.allclose(
                    df_data[f"{label}_y"].to_numpy()[0:n], correct_values[:, 1]
                )


def test_experiment_to_excel_trial_data_format(
    experiment_with_results: Experiment, tmp_path: pathlib.Path
) -> None:
    # export to an Excel file with a sheet for each trial
    excel_file = tmp_path / "export.xlsx"
    experiment_with_results.save_excel(str(excel_file), data_format="trial")
    stats: pd.DataFrame = experiment_with_results.stats
    # import this Excel file again
    exp = Experiment(str(excel_file))
    assert exp.metadata == experiment_with_results.metadata
    assert exp.display_options == experiment_with_results.display_options
    assert exp.trial_list == experiment_with_results.trial_list
    assert exp.trial_handler_with_results is None
    assert exp.has_unsaved_changes is True
    assert exp.filename == str(excel_file.with_suffix(".psydat"))
    # check that results sheets in Excel are consistent with stats dataframe
    dfs = pd.read_excel(excel_file, sheet_name=None)
    df_stats = dfs["statistics"]
    # convert x,y columns back to single (x,y) tuple column
    df_stats["center_pos"] = list(zip(df_stats.center_pos_x, df_stats.center_pos_y))
    df_stats.drop(columns=["center_pos_x", "center_pos_y"], inplace=True)
    df_stats["target_pos"] = list(zip(df_stats.target_pos_x, df_stats.target_pos_y))
    df_stats.drop(columns=["target_pos_x", "target_pos_y"], inplace=True)
    for name in df_stats:
        for a, b in zip(stats[name], df_stats[name]):
            assert np.allclose(a, b, equal_nan=True)
    n_trials = sum([trial["weight"] for trial in experiment_with_results.trial_list])
    assert len(dfs) == 4 + n_trials
    # check that excel trial data is consistent with stats dataframe
    n_center_targets_to_check = sum(
        [
            trial["weight"]
            * trial["num_targets"]
            * (0 if trial["automove_cursor_to_center"] else 1)
            for trial in experiment_with_results.trial_list
        ]
    )
    n_center_targets_checked = 0
    n_outer_targets_to_check = sum(
        [
            trial["weight"] * trial["num_targets"]
            for trial in experiment_with_results.trial_list
        ]
    )
    n_outer_targets_checked = 0
    i_row = -1  # track which row of df we should compare with
    for i_trial in range(n_trials):
        # this contains data for all targets from this trial
        df_data = dfs[f"{i_trial}"]
        # find the locations where the target changes
        indices_where_target_changes = df_data.index[
            df_data.i_target.diff() != 0
        ].values.tolist()
        indices_where_target_changes.append(df_data.index[-1] + 1)
        # iterate over each chunk of data with a single target
        for start, end in zip(
            indices_where_target_changes, indices_where_target_changes[1:]
        ):
            df_target = df_data.loc[start : end - 1]
            i_target = df_target.i_target.iloc[0]
            if i_target >= 0:
                dest = "target"
                # increment row counter each time we see a new (outer) target in the excel data
                i_row += 1
            elif i_target == -1:
                dest = "center"
            else:
                dest = None
            if dest is not None:
                # target data from target display time
                # get correct timestamps
                ts_correct = stats[f"to_{dest}_timestamps"][i_row]
                # get imported timestamps
                ts = df_target.timestamps.to_numpy()
                assert np.allclose(ts, ts_correct)
                # get correct mouse positions
                xys = stats[f"to_{dest}_mouse_positions"][i_row]
                n = xys.shape[0]
                if dest == "target" or (dest == "center" and n > 0):
                    assert np.allclose(
                        df_target["mouse_positions_x"].to_numpy(), xys[:, 0]
                    )
                    assert np.allclose(
                        df_target["mouse_positions_y"].to_numpy(), xys[:, 1]
                    )
                    if dest == "target":
                        n_outer_targets_checked += 1
                    elif dest == "center":
                        n_center_targets_checked += 1
            else:
                # data from where no target is visible: should also test this!
                pass
    assert n_outer_targets_checked == n_outer_targets_to_check
    assert n_center_targets_checked == n_center_targets_to_check


def test_experiment_to_excel_invalid_data_format(
    experiment_with_results: Experiment, tmp_path: pathlib.Path
) -> None:
    excel_file = tmp_path / "export.xlsx"
    with pytest.raises(RuntimeError):
        experiment_with_results.save_excel(str(excel_file), data_format="invalid")


def test_experiment_to_json(
    experiment_with_results: Experiment, tmp_path: pathlib.Path
) -> None:
    # export to a json file
    json_file = tmp_path / "export.json"
    experiment_with_results.save_json(str(json_file))
    # import this json file again
    exp = Experiment(str(json_file))
    assert exp.metadata == experiment_with_results.metadata
    assert exp.display_options == experiment_with_results.display_options
    assert exp.trial_list == experiment_with_results.trial_list
    assert exp.trial_handler_with_results is None
    assert exp.has_unsaved_changes is True
    assert exp.filename == str(json_file.with_suffix(".psydat"))


def test_experiment_invalid_file(tmp_path: pathlib.Path) -> None:
    # file doesn't exist
    with pytest.raises(ValueError):
        Experiment("I don't exist!")

    # file exists and has psydat extension but is garbage
    file = tmp_path / "invalid.psydat"
    file.write_text("beep boop")
    with pytest.raises(pickle.PickleError):
        Experiment(str(file))

    # file exists and has xlsx extension but is garbage
    file = tmp_path / "invalid.xlsx"
    file.write_text("beep boop")
    with pytest.raises(ValueError):
        Experiment(str(file))


def test_experiment_empty_trialhandler() -> None:
    # construct an empty TrialHandlerExt: no trials, no extraInfo dict
    empty_th = TrialHandlerExt([], 1)
    # this is what gets constructed from an empty trial list:
    assert empty_th.trialList == [None]
    assert empty_th.extraInfo is None
    experiment = Experiment()
    experiment.import_and_validate_trial_handler(empty_th)
    # defaults are used for missing metadata and display_options
    assert experiment.metadata == default_metadata()
    assert experiment.display_options == default_display_options()
    assert len(experiment.trial_list) == 0
