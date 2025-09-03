from __future__ import annotations

from psychopy.hardware import joystick
from psychopy.visual.window import Window

from vstt import joystick_wrapper


def have_joystick() -> bool:
    if hasattr(joystick, "getNumJoysticks"):
        return joystick.getNumJoysticks() > 0
    if hasattr(joystick.Joystick, "getAvailableDevices"):
        return len(joystick.Joystick.getAvailableDevices()) > 0
    return False


def test_joystick_wrapper(window: Window) -> None:
    # check that calling repeatedly doesn't raise an exception
    if have_joystick():
        assert joystick_wrapper.get_joystick() is not None
        assert joystick_wrapper.get_joystick() is not None
    else:
        assert joystick_wrapper.get_joystick() is None
        assert joystick_wrapper.get_joystick() is None
