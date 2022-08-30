from sys import platform
from typing import List
from typing import Tuple

import numpy as np
import pyautogui
import pytest
from motor_task_prototype.geom import points_on_circle
from motor_task_prototype.task import new_experiment_from_dicts
from motor_task_prototype.trial import default_trial
from motor_task_prototype.vis import default_display_options
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


def noise(scale: float = 0.01) -> float:
    return scale * (np.random.random_sample() - 0.1)


def make_mouse_positions(
    pos: Tuple[float, float], time_points: np.ndarray
) -> List[Tuple[float, float]]:
    return [(pos[0] * t + noise(), pos[1] * t + noise()) for t in time_points]


def make_timestamps(n_min: int = 8, n_max: int = 20) -> np.ndarray:
    return np.linspace(0.0, 1.0, np.random.randint(n_min, n_max))


@pytest.fixture
def experiment_no_results() -> TrialHandlerExt:
    trial = default_trial()
    # disable sounds due to issues with sounds within tests on linux
    trial["play_sound"] = False
    trial["play_sound"] = False
    trial["inter_target_duration"] = 0.0
    display_options = default_display_options()
    return new_experiment_from_dicts([trial], display_options)


@pytest.fixture
def experiment_with_results() -> TrialHandlerExt:
    trial = default_trial()
    trial["weight"] = 3
    trial["automove_cursor_to_center"] = False
    display_options = default_display_options()
    exp = new_experiment_from_dicts([trial], display_options)
    for trial in exp:
        to_target_timestamps = []
        to_center_timestamps = []
        to_target_mouse_positions = []
        to_center_mouse_positions = []
        target_pos = points_on_circle(
            trial["num_targets"], trial["target_distance"], include_centre=False
        )
        for pos in target_pos:
            to_target_timestamps.append(make_timestamps())
            to_target_mouse_positions.append(
                make_mouse_positions(pos, to_target_timestamps[-1])
            )
            to_center_timestamps.append(make_timestamps())
            to_center_mouse_positions.append(
                list(reversed(make_mouse_positions(pos, to_center_timestamps[-1])))
            )
        exp.addData("target_pos", np.array(target_pos))
        exp.addData("to_target_timestamps", np.array(to_target_timestamps))
        exp.addData("to_target_mouse_positions", np.array(to_target_mouse_positions))
        exp.addData("to_center_timestamps", np.array(to_center_timestamps))
        exp.addData("to_center_mouse_positions", np.array(to_center_mouse_positions))
    return exp
