import motor_task_prototype.meta as mtpmeta


def test_metadata_labels() -> None:
    metadata = mtpmeta.default_metadata()
    labels = mtpmeta.metadata_labels()
    assert len(metadata) == len(labels)
    assert metadata.keys() == labels.keys()
