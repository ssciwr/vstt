from __future__ import annotations

import json
import pathlib
import pickle
from typing import Any

import pandas as pd
from psychopy.data import TrialHandlerExt
from psychopy.misc import fromFile

from vstt.display import default_display_options
from vstt.display import import_display_options
from vstt.meta import default_metadata
from vstt.meta import import_metadata
from vstt.stats import append_stats_data_to_excel
from vstt.stats import stats_dataframe
from vstt.trial import default_trial
from vstt.trial import import_and_validate_trial


class Experiment:
    def __init__(self, filename: str | None = None):
        self.filename = "default-experiment.psydat"
        self.has_unsaved_changes = False
        self.metadata = default_metadata()
        self.display_options = default_display_options()
        self.trial_list = [default_trial()]
        self.trial_handler_with_results: TrialHandlerExt | None = None
        self.stats: pd.DataFrame | None = None
        if filename is not None:
            self.load_file(filename)

    def create_trialhandler(self) -> TrialHandlerExt:
        for index, trial in enumerate(self.trial_list):
            self.trial_list[index] = import_and_validate_trial(trial)
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

    def _as_dict(self) -> dict[str, Any]:
        return {
            "metadata": self.metadata,
            "display_options": self.display_options,
            "trial_list": self.trial_list,
        }

    def load_file(self, filename: str) -> None:
        suffix = pathlib.Path(filename).suffix
        if suffix == ".xlsx":
            self.load_excel(filename)
        elif suffix == ".json":
            self.load_json(filename)
        else:
            # assume psydat format by default
            self.load_psydat(filename)

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

    def save_excel(self, filename: str, data_format: str) -> None:
        """
        data_format can be
        - "trial": one sheet of data exported per trial
        - "target: one sheet of data exported per target
        """
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"
        with pd.ExcelWriter(filename) as writer:
            pd.DataFrame([self.metadata]).to_excel(
                writer, sheet_name="metadata", index=False
            )
            pd.DataFrame([self.display_options]).to_excel(
                writer, sheet_name="display_options", index=False
            )
            pd.DataFrame(self.trial_list).to_excel(
                writer, sheet_name="trial_list", index=False
            )
            if self.stats is not None:
                append_stats_data_to_excel(self.stats, writer, data_format)

    def load_excel(self, filename: str) -> None:
        dfs = pd.read_excel(filename, ["metadata", "display_options", "trial_list"])
        self.import_and_validate_dicts(
            filename,
            dfs["metadata"].to_dict("records")[0],
            dfs["display_options"].to_dict("records")[0],
            dfs["trial_list"].to_dict("records"),
        )

    def save_json(self, filename: str) -> None:
        if not filename.endswith(".json"):
            filename += ".json"
        with open(filename, "w") as f:
            json.dump(self._as_dict(), f)

    def load_json(self, filename: str) -> None:
        with open(filename) as f:
            d = json.load(f)
        self.import_and_validate_dicts(
            filename, d["metadata"], d["display_options"], d["trial_list"]
        )

    def import_and_validate_dicts(
        self,
        filename: str,
        metadata_dict: dict,
        display_options_dict: dict,
        trial_dict_list: list[dict],
    ) -> None:
        self.metadata = import_metadata(metadata_dict)
        self.display_options = import_display_options(display_options_dict)
        self.trial_list = [
            import_and_validate_trial(trial_dict) for trial_dict in trial_dict_list
        ]
        self.trial_handler_with_results = None
        self.stats = None
        self.has_unsaved_changes = True
        self.filename = str(pathlib.Path(filename).with_suffix(".psydat"))

    def import_and_validate_trial_handler(self, trial_handler: TrialHandlerExt) -> None:
        # psychopy trial handler converts empty trial list [] -> [None]
        if trial_handler.trialList == [None]:
            trial_handler.trialList = []
        for index, trial in enumerate(trial_handler.trialList):
            trial_handler.trialList[index] = import_and_validate_trial(trial)
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
            self.stats = stats_dataframe(trial_handler)
        else:
            self.trial_handler_with_results = None
            self.stats = None
