"""
Wrapper around psychopy Joystick to work around psychopy bug

For pyglet backend psychopy Joystick constructor calls .open() on the pyglet input device.
If this device is already open (i.e. we already created a Joystick) then pyglet raises an exception.
Here we keep track of the current joystick object and attempt to close the underlying pyglet device.
"""

from __future__ import annotations

import logging

from psychopy.hardware import joystick
from pyglet.input import DeviceOpenException

js: joystick.Joystick | None = None


def _close_open_device() -> None:
    global js
    if js is None:
        return
    try:
        js._device.close()  # attempt to close pyglet device
    except Exception as e:
        logging.warning(f"Failed to close pyglet joystick device: {e}")
        logging.exception(e)


def _updated_joystick() -> joystick.Joystick:
    try:
        return joystick.Joystick(0)
    except DeviceOpenException:
        _close_open_device()
        return joystick.Joystick(0)


def get_joystick() -> joystick.Joystick | None:
    global js
    if joystick.getNumJoysticks() == 0:
        return None
    try:
        js = _updated_joystick()
    except Exception as e:
        logging.warning("Failed to get Joystick")
        logging.exception(e)
        return None
    return js
