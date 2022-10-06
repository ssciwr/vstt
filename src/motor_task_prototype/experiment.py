from __future__ import annotations

import pickle
from typing import Optional

from motor_task_prototype.display import default_display_options
from motor_task_prototype.display import import_display_options
from motor_task_prototype.meta import default_metadata
from motor_task_prototype.meta import import_metadata
from motor_task_prototype.trial import default_trial
from motor_task_prototype.trial import validate_trial
from psychopy.data import TrialHandlerExt
from psychopy.misc import fromFile


class MotorTaskExperiment:
    def __init__(self, filename: Optional[str] = None):
        if filename is not None:
            self.load_psydat(filename)
            return

        self.filename = "default-experiment.psydat"
        self.has_unsaved_changes = False
        self.metadata = default_metadata()
        self.display_options = default_display_options()
        self.trial_list = [default_trial()]
        self.trial_handler_with_results: Optional[TrialHandlerExt] = None

    def create_trialhandler(self) -> TrialHandlerExt:
        for trial in self.trial_list:
            validate_trial(trial)
        return TrialHandlerExt(
            self.trial_list,
            nReps=1,
            method="sequential",
            originPath=-1,
            extraInfo={
                "display_options": self.display_options,
                "metadata": self.metadata,
            },
        )

    def clear_results(self) -> None:
        self.trial_handler_with_results = None

    def save_psydat(self, filename: str) -> None:
        if not filename.endswith(".psydat"):
            filename += ".psydat"

        if self.trial_handler_with_results is not None:
            # save existing trial handler with results, only update its extraInfo dict
            self.trial_handler_with_results.extraInfo = {
                "display_options": self.display_options,
                "metadata": self.metadata,
            }
            self.trial_handler_with_results.saveAsPickle(
                filename, fileCollisionMethod="overwrite"
            )
        else:
            # create a new trial handler to save this experiment
            trial_handler = self.create_trialhandler()
            # temporary hack as the psyschopy function only saves if there are results!
            with open(filename, "wb") as f:
                pickle.dump(trial_handler, f)
        self.filename = filename
        self.has_unsaved_changes = False

    def load_psydat(self, filename: str) -> None:
        self.import_and_validate_trial_handler(fromFile(filename))
        self.filename = filename
        self.has_unsaved_changes = False

    def import_and_validate_trial_handler(self, trial_handler: TrialHandlerExt) -> None:
        # psychopy trial handler converts empty trial list [] -> [None]
        if trial_handler.trialList == [None]:
            trial_handler.trialList = []
        for trial in trial_handler.trialList:
            validate_trial(trial)
        self.trial_list = trial_handler.trialList
        if not trial_handler.extraInfo:
            trial_handler.extraInfo = {}
        self.metadata = import_metadata(
            trial_handler.extraInfo.get("metadata", default_metadata())
        )
        self.display_options = import_display_options(
            trial_handler.extraInfo.get("display_options", default_display_options())
        )
        if trial_handler.finished:
            self.trial_handler_with_results = trial_handler
        else:
            self.trial_handler_with_results = None
