from __future__ import annotations

import vstt


def test_metadata_labels() -> None:
    metadata = vstt.meta.default_metadata()
    labels = vstt.meta.metadata_labels()
    assert len(metadata) == len(labels)
    assert metadata.keys() == labels.keys()


def test_import_metadata() -> None:
    # valid metadata imported
    valid_dict = {
        "name": "bob",
        "subject": "trial",
        "date": "1/2/3",
        "author": "jim",
        "display_title": "title",
        "display_text1": "t1",
        "display_text2": "t2",
        "display_text3": "t3",
        "display_text4": "t4",
        "display_duration": 123,
        "show_delay_countdown": False,
        "enter_to_skip_delay": False,
    }
    metadata = vstt.meta.import_metadata(valid_dict)
    assert metadata == valid_dict
    # all keys missing -> replaced with defaults
    metadata = vstt.meta.import_metadata({})
    assert metadata == vstt.meta.default_metadata()
    # valid keys present but values have wrong type:
    #   - coerced to correct type if legal to do so
    #   - otherwise replaced with defaults
    metadata = vstt.meta.import_metadata(
        {"name": 12, "data": 2.4, "author": [1, 2, 3], "whoops": "ok"}
    )
    assert metadata["name"] == "12"
    assert metadata["author"] == "[1, 2, 3]"
    # unknown keys are ignored
    assert "data" not in metadata
    assert "whoops" not in metadata
