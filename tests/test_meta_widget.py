import motor_task_prototype.meta as mtpmeta
from motor_task_prototype.meta_widget import MetadataWidget
from PyQt5 import QtWidgets
from PyQt5.QtTest import QTest


def test_metadata_widget() -> None:
    widget = MetadataWidget(None)
    # initially has empty metadata
    assert widget.get_metadata() == mtpmeta.empty_metadata()
    assert widget.unsaved_changes is False
    # set all to defaults
    widget.set_metadata(mtpmeta.default_metadata())
    assert widget.get_metadata() == mtpmeta.default_metadata()
    assert widget.unsaved_changes is False
    # reset to empty, then type in each line edit
    widget.set_metadata(mtpmeta.empty_metadata())
    assert widget.unsaved_changes is False
    for key in mtpmeta.empty_metadata().keys():
        line_edit = widget._widgets[key]
        assert line_edit is not None
        assert type(line_edit) is QtWidgets.QLineEdit
        assert widget.get_metadata()[key] == ""  # type: ignore
        QTest.keyClicks(line_edit, key)
        assert widget.get_metadata()[key] == key  # type: ignore
        assert widget.unsaved_changes is True
    for key, value in widget.get_metadata().items():
        assert value == key
