from __future__ import annotations

import motor_task_prototype.meta as mtpmeta


def test_metadata_labels() -> None:
    metadata = mtpmeta.default_metadata()
    labels = mtpmeta.metadata_labels()
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
    }
    metadata = mtpmeta.import_metadata(valid_dict)
    assert metadata == valid_dict
    # all keys missing -> replaced with defaults
    metadata = mtpmeta.import_metadata({})
    assert metadata == mtpmeta.default_metadata()
    # valid keys present but values have wrong type -> replaced with defaults
    metadata = mtpmeta.import_metadata({"name": 12, "data": 2.4, "author": [1, 2, 3]})
    assert metadata == mtpmeta.default_metadata()
    # invalid keys are ignored
    metadata = mtpmeta.import_metadata({"whoops": "ok"})
    assert "whoops" not in metadata
