from typing import List
from typing import Optional

from motor_task_prototype import vis as mtpvis
from motor_task_prototype.display import default_display_options
from motor_task_prototype.meta import default_metadata
from motor_task_prototype.meta import empty_metadata
from motor_task_prototype.meta import MotorTaskMetadata
from motor_task_prototype.trial import default_trial
from motor_task_prototype.trial import MotorTaskTrial
from motor_task_prototype.trial import validate_trial
from psychopy.data import TrialHandlerExt
from psychopy.gui import fileOpenDlg
from psychopy.gui import fileSaveDlg
from psychopy.misc import fromFile


def new_default_experiment() -> TrialHandlerExt:
    return TrialHandlerExt(
        [default_trial()],
        nReps=1,
        method="sequential",
        originPath=-1,
        extraInfo={
            "display_options": default_display_options(),
            "metadata": default_metadata(),
        },
    )


def validate_experiment_inplace(experiment: TrialHandlerExt) -> None:
    for trial in experiment.trialList:
        # psychopy trial handler converts empty trial list [] -> [None]
        if trial is not None:
            validate_trial(trial)
    if not experiment.extraInfo:
        experiment.extraInfo = {}
    if "display_options" not in experiment.extraInfo:
        experiment.extraInfo["display_options"] = default_display_options()
    if "metadata" not in experiment.extraInfo:
        experiment.extraInfo["metadata"] = empty_metadata()


def get_experiment_filename_from_user() -> Optional[str]:
    filename = fileOpenDlg(allowed="Psydat files (*.psydat)")
    if filename is None or len(filename) < 1:
        return None
    return filename[0]


def import_experiment_from_file(filename: str) -> TrialHandlerExt:
    experiment = fromFile(filename)
    validate_experiment_inplace(experiment)
    return experiment


def new_experiment_from_trialhandler(
    experiment: TrialHandlerExt,
) -> Optional[TrialHandlerExt]:
    if experiment.trialList[0] is None:
        # psychopy converts an empty triallist into a list with a None element
        return None
    validate_experiment_inplace(experiment)
    return TrialHandlerExt(
        experiment.trialList,
        nReps=1,
        method=experiment.method,
        originPath=-1,
        extraInfo=experiment.extraInfo,
    )


def new_experiment_from_dicts(
    trials: List[MotorTaskTrial],
    display_options: mtpvis.MotorTaskDisplayOptions,
    metadata: MotorTaskMetadata,
) -> TrialHandlerExt:
    for trial in trials:
        validate_trial(trial)
    return TrialHandlerExt(
        trials,
        nReps=1,
        method="sequential",
        originPath=-1,
        extraInfo={"display_options": display_options, "metadata": metadata},
    )


def save_experiment(experiment: TrialHandlerExt) -> bool:
    filename = fileSaveDlg(
        prompt="Save trial conditions and results as psydat file",
        allowed="Psydat files (*.psydat)",
    )
    if filename is not None:
        experiment.saveAsPickle(filename, fileCollisionMethod="overwrite")
        return True
    return False
