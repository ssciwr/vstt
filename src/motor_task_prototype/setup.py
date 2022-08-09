from dataclasses import dataclass
from typing import Optional

import motor_task_prototype as mtp
import wx
from motor_task_prototype.trial import get_trial_from_psydat
from motor_task_prototype.trial import get_trial_from_user
from motor_task_prototype.trial import MotorTaskTrial
from psychopy.data import TrialHandlerExt
from psychopy.gui import fileOpenDlg
from psychopy.misc import fromFile


@dataclass
class UserChoices:
    run_task: bool
    conditions: Optional[MotorTaskTrial]
    trials: Optional[TrialHandlerExt]


def setup() -> Optional[UserChoices]:
    app = wx.App(False)
    app.MainLoop()
    title = f"Motor Task Prototype {mtp.__version__}"
    dialog = wx.SingleChoiceDialog(
        None,
        f"{title}\n\nhttps://github.com/ssciwr/motor-task-prototype",
        title,
        [
            "Create and run a new trial",
            "Import and run an existing trial",
            "Display existing trial results",
            "Exit",
        ],
    )
    result = dialog.ShowModal()
    selection = dialog.GetSelection()
    dialog.Destroy()
    if result != wx.ID_OK:
        return None
    if selection == 0:
        return UserChoices(True, get_trial_from_user(), None)
    elif selection == 1:
        filename = fileOpenDlg(allowed="Psydat files (*.psydat)")
        if filename is None or len(filename) < 1:
            return None
        return UserChoices(True, get_trial_from_psydat(filename[0]), None)
    elif selection == 2:
        filename = fileOpenDlg(allowed="Psydat files (*.psydat)")
        if filename is None or len(filename) < 1:
            return None
        return UserChoices(False, None, fromFile(filename[0]))
    elif selection == 3:
        return None
    return None
