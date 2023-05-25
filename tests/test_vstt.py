from __future__ import annotations

import vstt


def test_vstt_import() -> None:
    assert len(vstt.__version__) > 0
