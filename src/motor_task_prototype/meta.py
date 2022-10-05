from __future__ import annotations

from typing import Dict

import motor_task_prototype.common as mtpcommon
from motor_task_prototype.types import MotorTaskMetadata


def empty_metadata() -> MotorTaskMetadata:
    return {
        "name": "",
        "subject": "",
        "date": "",
        "author": "",
        "display_title": "",
        "display_text1": "",
        "display_text2": "",
        "display_text3": "",
        "display_text4": "",
    }


def default_metadata() -> MotorTaskMetadata:
    return {
        "name": "Experiment",
        "subject": "Joe Smith",
        "date": "2022/01/01",
        "author": "Author",
        "display_title": "Welcome to the experiment",
        "display_text1": "When a target is presented, "
        "you will hear an audible tone and the target circle will turn red.",
        "display_text2": "Try to move the cursor to the red circle "
        "as quickly and accurately as you can.",
        "display_text3": "You can abort the experiment at any time "
        "by pressing the Escape key.",
        "display_text4": "Otherwise, press Enter " "when you are ready to begin.",
    }


def metadata_labels() -> Dict:
    return {
        "name": "Experiment Name",
        "subject": "Subject Name",
        "date": "Date",
        "author": "Author",
        "display_title": "Title text to display",
        "display_text1": "Main text line 1",
        "display_text2": "Main text line 2",
        "display_text3": "Main text line 3",
        "display_text4": "Main text line 4",
    }


def import_metadata(metadata_dict: dict) -> MotorTaskMetadata:
    return mtpcommon.import_typed_dict(metadata_dict, default_metadata())
