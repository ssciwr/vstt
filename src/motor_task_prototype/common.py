from __future__ import annotations

import copy
import logging
from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

import motor_task_prototype.types as mtptypes

MtpTypedDict = TypeVar(
    "MtpTypedDict",
    mtptypes.MotorTaskTrial,
    mtptypes.MotorTaskMetadata,
    mtptypes.MotorTaskDisplayOptions,
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
    input_dict: Dict, default_typed_dict: MtpTypedDict
) -> MtpTypedDict:
    # start with a valid typed dict with default values
    output_dict = copy.deepcopy(default_typed_dict)
    for key, default_value in output_dict.items():
        if key in input_dict:
            # import all valid keys from input_dict
            correct_type = type(default_value)
            value = input_dict[key]
            if _has_valid_type(value, correct_type):
                output_dict[key] = correct_type(value)  # type: ignore
            else:
                logging.warning(
                    f"Key '{key}' invalid: expected {correct_type}, got {type(value)} '{value}'"
                )
        else:
            # warn if a key is missing
            logging.warning(f"Key '{key}' missing, using default '{default_value}'")
    for key in input_dict:
        if key not in output_dict:
            # warn if there are any unknown keys in the input dict
            logging.warning(f"Ignoring unknown key '{key}'")
    return output_dict
