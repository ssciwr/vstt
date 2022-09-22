from dataclasses import dataclass
from typing import List
from typing import Optional

import motor_task_prototype as mtp
from motor_task_prototype.display import get_display_options_from_user
from motor_task_prototype.meta import get_metadata_from_user
from motor_task_prototype.task import new_experiment_from_dicts
from motor_task_prototype.task import new_experiment_from_trialhandler
from motor_task_prototype.trial import describe_trial
from motor_task_prototype.trial import describe_trials
from motor_task_prototype.trial import get_trial_from_user
from motor_task_prototype.trial import MotorTaskTrial
from psychopy import core
from psychopy.data import TrialHandlerExt
from psychopy.gui import DlgFromDict
from psychopy.gui import fileOpenDlg
from psychopy.gui.qtgui import ensureQtApp
from psychopy.misc import fromFile
from PyQt5 import QtWidgets


@dataclass
class UserChoices:
    run_task: bool
    experiment: TrialHandlerExt
    display_trial_indices: Optional[List[int]]


def get_experiment_from_user() -> TrialHandlerExt:
    metadata = get_metadata_from_user()
    trials: List[MotorTaskTrial] = []
    initial_trial = None
    add_another_trial = True
    while add_another_trial:
        if len(trials) > 0:
            initial_trial = trials[-1]
        trials.append(get_trial_from_user(initial_trial))
        yes_no = QtWidgets.QMessageBox.question(
            None,
            "Add another trial?",
            "Trials in experiment:\n\n"
            + describe_trials(trials)
            + "\n\nAdd another trial to the experiment?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if yes_no == QtWidgets.QMessageBox.No:
            add_another_trial = False
    display_options = get_display_options_from_user()
    return new_experiment_from_dicts(trials, display_options, metadata)


def get_trial_list_index_from_user(trial_list: List[MotorTaskTrial]) -> int:
    if len(trial_list) == 1:
        # only one possible choice
        return 0
    trial_list_indices = [
        f"{index} ({describe_trial(trial)})" for index, trial in enumerate(trial_list)
    ]
    choices = {"Trial Block": trial_list_indices}
    dialog = DlgFromDict(choices, title="Select trial block to display")
    if not dialog.OK:
        core.quit()
    return int(str(choices["Trial Block"]).split(" ")[0])


def get_trial_indices_from_user(
    experiment: TrialHandlerExt, trial_list_index: int
) -> List[int]:
    trial_indices = [i for i in range(experiment.trialList[trial_list_index]["weight"])]
    # order that trials occur in experiment may not be the order they are defined in trialList
    # assume 1 repetition of experiment
    i_rep = 0
    result_trial_indices = []
    for result_index, condition_index in enumerate(experiment.sequenceIndices):
        if condition_index[i_rep] == trial_list_index:
            result_trial_indices.append(result_index)
    if len(result_trial_indices) == 1:
        # only one possible choice
        return result_trial_indices
    choices = {"Trial": ["All"] + [str(i) for i in trial_indices]}
    dialog = DlgFromDict(
        choices,
        title="Select trials(s) to display from block",
    )
    if not dialog.OK:
        core.quit()
    if choices["Trial"] == "All":
        return result_trial_indices
    return [result_trial_indices[int(str(choices["Trial"]))]]


def setup() -> Optional[UserChoices]:
    ensureQtApp()
    title = f"Motor Task Prototype {mtp.__version__}"
    options = [
        "Create and run a new experiment",
        "Import and run an existing experiment",
        "Display existing experiment results",
        "Exit",
    ]
    result, ok = QtWidgets.QInputDialog.getItem(
        None,
        title,
        f"{title}\n\nhttps://ssciwr.github.io/motor-task-prototype/",
        options,
        0,
        False,
    )
    if not ok:
        return None
    selection = options.index(result)
    if selection == 0:
        return UserChoices(True, get_experiment_from_user(), None)
    elif selection == 1:
        filename = fileOpenDlg(allowed="Psydat files (*.psydat)")
        if filename is None or len(filename) < 1:
            return None
        return UserChoices(
            True, new_experiment_from_trialhandler(fromFile(filename[0])), None
        )
    elif selection == 2:
        filename = fileOpenDlg(allowed="Psydat files (*.psydat)")
        if filename is None or len(filename) < 1:
            return None
        experiment = fromFile(filename[0])
        trial_list_index = get_trial_list_index_from_user(experiment.trialList)
        trial_indices = get_trial_indices_from_user(experiment, trial_list_index)
        display_options = None
        if experiment.extraInfo and "display_options" in experiment.extraInfo:
            display_options = experiment.extraInfo["display_options"]
        experiment.extraInfo["display_options"] = get_display_options_from_user(
            display_options
        )
        return UserChoices(False, experiment, trial_indices)
    elif selection == 3:
        return None
    return None
