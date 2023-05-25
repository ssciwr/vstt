from __future__ import annotations

from psychopy.hardware import joystick
from psychopy.visual.window import Window
from vstt import joystick_wrapper


def test_joystick_wrapper(window: Window) -> None:
    # check that calling repeatedly doesn't raise an exception
    if joystick.getNumJoysticks() > 0:
        assert joystick_wrapper.get_joystick() is not None
        assert joystick_wrapper.get_joystick() is not None
    else:
        assert joystick_wrapper.get_joystick() is None
        assert joystick_wrapper.get_joystick() is None
