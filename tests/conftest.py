from sys import platform

import numpy as np
import pyautogui
import pytest
from motor_task_prototype.geom import points_on_circle
from motor_task_prototype.trial import default_trial
from psychopy.data import TrialHandlerExt
from psychopy.visual.window import Window


@pytest.fixture(scope="session", autouse=True)
# autouse means all tests use this fixture
# session scope means it is only called once
# so this fixture runs once before any tests
def tests_init() -> None:
    # work around for PsychHID-WARNING about X11 not being initialized on linux
    if platform == "linux":
        import ctypes

        xlib = ctypes.cdll.LoadLibrary("libX11.so")
        xlib.XInitThreads()
    # if FAILSAFE is True, pyautogui raises an exception
    # if the cursor is in the top-left corner:
    # https://pyautogui.readthedocs.io/en/latest/quickstart.html#fail-safes
    pyautogui.FAILSAFE = False


# fixture to create a wxPython Window for testing gui functions
# GLFW backend used for tests as it works better with Xvfb
@pytest.fixture()
def window() -> Window:
    window = Window(
        fullscr=True,
        units="height",
        winType="glfw",
    )
    # yield is like return except control flow returns here afterwards
    yield window
    # clean up window
    window.close()


@pytest.fixture
def fake_trial() -> TrialHandlerExt:
    th = TrialHandlerExt([default_trial()], nReps=1, method="sequential", originPath=-1)
    for trial in th:
        timestamps = []
        mouse_positions = []
        target_pos = points_on_circle(
            trial["num_targets"], trial["target_distance"], include_centre=False
        )
        for pos in target_pos:
            timestamps.append([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
            mouse_positions.append(
                [
                    (0.0, 0.0),
                    (0.001 + pos[0] * 0.1, pos[1] * 0.1),
                    (pos[0] * 0.18, pos[1] * 0.23 + 0.0008),
                    (pos[0] * 0.43, pos[1] * 0.37),
                    (0.007 + pos[0] * 0.76, pos[1] * 0.87 - 0.005),
                    pos,
                ]
            )
        th.addData("target_pos", np.array(target_pos))
        th.addData("timestamps", np.array(timestamps))
        th.addData("mouse_positions", np.array(mouse_positions))
    return th
