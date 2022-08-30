from dataclasses import dataclass
from typing import Optional

import motor_task_prototype as mtp
import wx
from motor_task_prototype.task import new_experiment_from_dicts
from motor_task_prototype.task import new_experiment_from_trialhandler
from motor_task_prototype.trial import get_trial_from_user
from motor_task_prototype.vis import get_display_options_from_user
from psychopy.data import TrialHandlerExt
from psychopy.gui import fileOpenDlg
from psychopy.misc import fromFile


@dataclass
class UserChoices:
    run_task: bool
    experiment: TrialHandlerExt


def setup() -> Optional[UserChoices]:
    app = wx.App(False)
    app.MainLoop()
    title = f"Motor Task Prototype {mtp.__version__}"
    dialog = wx.SingleChoiceDialog(
        None,
        f"{title}\n\nhttps://github.com/ssciwr/motor-task-prototype",
        title,
        [
            "Create and run a new experiment",
            "Import and run an existing experiment",
            "Display existing experiment results",
            "Exit",
        ],
    )
    result = dialog.ShowModal()
    selection = dialog.GetSelection()
    dialog.Destroy()
    if result != wx.ID_OK:
        return None
    if selection == 0:
        trials = [get_trial_from_user()]
        display_options = get_display_options_from_user()
        return UserChoices(True, new_experiment_from_dicts(trials, display_options))
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
