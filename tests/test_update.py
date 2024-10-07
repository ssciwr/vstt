from __future__ import annotations

import sys

from pytest import MonkeyPatch

import vstt
from vstt.update import check_for_new_version
from vstt.update import do_pip_upgrade


def test_new_version_available(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(vstt, "__version__", "0.0.0")
    available, message = check_for_new_version()
    assert available is True
    assert "0.0.0" in message
    assert "upgrade" in message
    monkeypatch.setattr(vstt, "__version__", "9999.0.0")
    available, message = check_for_new_version()
    assert available is False
    assert "latest version" in message
    monkeypatch.setattr(vstt, "__version__", "imnot-a-valid-version!")
    available, message = check_for_new_version()
    assert available is False
    assert "error" in message


def test_do_pip_upgrade(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "executable", "abc123_i_dont_exist")
    success, message = do_pip_upgrade()
    assert success is False
    assert "error" in message
