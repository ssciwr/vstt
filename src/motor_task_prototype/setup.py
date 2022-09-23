from dataclasses import dataclass
from typing import List
from typing import Optional

import motor_task_prototype as mtp
from motor_task_prototype.display import get_display_options_from_user
from motor_task_prototype.meta import get_metadata_from_user
from motor_task_prototype.task import new_experiment_from_dicts
from motor_task_prototype.task import new_experiment_from_trialhandler
from motor_task_prototype.trial import describe_trials
from motor_task_prototype.trial import get_trial_from_user
from motor_task_prototype.trial import MotorTaskTrial
from psychopy.data import TrialHandlerExt
from psychopy.gui import fileOpenDlg
from psychopy.gui.qtgui import ensureQtApp
from psychopy.misc import fromFile
from PyQt5 import QtWidgets


@dataclass
class UserChoices:
    run_task: bool
    experiment: TrialHandlerExt


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
        return UserChoices(True, get_experiment_from_user())
    elif selection == 1:
        filename = fileOpenDlg(allowed="Psydat files (*.psydat)")
        if filename is None or len(filename) < 1:
            return None
        return UserChoices(
            True, new_experiment_from_trialhandler(fromFile(filename[0]))
        )
    elif selection == 2:
        filename = fileOpenDlg(allowed="Psydat files (*.psydat)")
        experiment = fromFile(filename[0])
        display_options = None
        if experiment.extraInfo and "display_options" in experiment.extraInfo:
            display_options = experiment.extraInfo["display_options"]
        experiment.extraInfo["display_options"] = get_display_options_from_user(
            display_options
        )
        if filename is None or len(filename) < 1:
            return None
        return UserChoices(False, experiment)
    elif selection == 3:
        return None
    return None
