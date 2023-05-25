from __future__ import annotations

import vstt


def test_has_valid_type() -> None:
    # type matches instance: valid
    for item in [5, 5.2, "str"]:
        assert vstt.common._has_valid_type(item, type(item))
    # float / int mismatches are also considered valid
    for number_value in [5, 5.2]:
        for number_type in [float, int]:
            assert vstt.common._has_valid_type(number_value, number_type)
    # other mismatches are invalid
    assert vstt.common._has_valid_type("5", int) is False
