from __future__ import annotations

import copy
import logging
from typing import Any
from typing import Mapping
from typing import Type
from typing import TypeVar

from vstt.vtypes import DisplayOptions
from vstt.vtypes import Metadata
from vstt.vtypes import Trial

VsttTypedDict = TypeVar(
    "VsttTypedDict",
    Trial,
    Metadata,
    DisplayOptions,
)


def _has_valid_type(var: Any, correct_type: Type) -> bool:
    if isinstance(var, correct_type):
        # var has the correct type
        return True
    if correct_type in (float, int) and type(var) in (float, int):
        # int instead of float or vice versa is ok
        return True
    return False


def import_typed_dict(
    input_dict: Mapping[str, Any], default_typed_dict: VsttTypedDict
) -> VsttTypedDict:
    # start with a valid typed dict with default values
    output_dict = copy.deepcopy(default_typed_dict)
    for key, default_value in output_dict.items():
        if key in input_dict:
            # import all valid keys from input_dict
            correct_type = type(default_value)
            value = input_dict[key]
            if not _has_valid_type(value, correct_type):
                logging.warning(
                    f"Key '{key}' invalid: expected {correct_type}, got {type(value)} '{value}'"
                )
            try:
                output_dict[key] = correct_type(value)  # type: ignore
            except ValueError:
                logging.warning(
                    f"Failed to coerce Key '{key}' with type {type(value)} to correct type {correct_type}"
                )
        else:
            # warn if a key is missing
            logging.warning(f"Key '{key}' missing, using default '{default_value}'")
    for key in input_dict:
        if key not in output_dict:
            # warn if there are any unknown keys in the input dict
            logging.warning(f"Ignoring unknown key '{key}'")
    return output_dict
