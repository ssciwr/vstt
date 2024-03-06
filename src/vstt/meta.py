from __future__ import annotations

import vstt


def default_metadata() -> vstt.vtypes.Metadata:
    return {
        "name": "Experiment",
        "subject": "Joe Smith",
        "date": "2022/01/01",
        "author": "Author",
        "display_title": "Welcome to the experiment",
        "display_text1": "When a target is presented the target circle will turn red.",
        "display_text2": "You will also hear an audible tone",
        "display_text3": "Try to move the cursor to the red circle "
        "as quickly and accurately as you can.",
        "display_text4": "You can abort the experiment at any time "
        "by pressing the Escape key.",
        "display_duration": 60,
        "show_delay_countdown": True,
        "enter_to_skip_delay": True,
    }


def metadata_labels() -> dict:
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
        "display_duration": "Display duration (seconds)",
        "show_delay_countdown": "Display a countdown",
        "enter_to_skip_delay": "Skip by pressing enter key",
    }


def import_metadata(metadata_dict: dict) -> vstt.vtypes.Metadata:
    return vstt.common.import_typed_dict(metadata_dict, default_metadata())
