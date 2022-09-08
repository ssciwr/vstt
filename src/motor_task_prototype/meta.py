import copy
import sys
from typing import Dict
from typing import Optional

from psychopy import core
from psychopy.gui import DlgFromDict

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

MotorTaskMetadata = TypedDict(
    "MotorTaskMetadata",
    {
        "name": str,
        "subject": str,
        "date": str,
        "author": str,
        "display_title": str,
        "display_text1": str,
        "display_text2": str,
        "display_text3": str,
        "display_text4": str,
    },
)


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


def get_metadata_from_user(
    initial_metadata: Optional[MotorTaskMetadata] = None,
) -> MotorTaskMetadata:
    if initial_metadata:
        metadata = copy.deepcopy(initial_metadata)
    else:
        metadata = default_metadata()
    dialog = DlgFromDict(
        metadata, title="Experiment metadata", labels=metadata_labels(), sortKeys=False
    )
    if not dialog.OK:
        core.quit()
    return metadata
