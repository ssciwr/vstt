from __future__ import annotations

import copy
import os
import sys
from typing import Tuple

import numpy as np
import pyautogui
import pytest
from motor_task_prototype.experiment import MotorTaskExperiment
from motor_task_prototype.geom import points_on_circle
from motor_task_prototype.trial import default_trial
from psychopy.gui.qtgui import ensureQtApp
from psychopy.visual.window import Window

# add tests helpers package location to path so tests can import gui_test_utils
sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))


@pytest.fixture(scope="session", autouse=True)
# autouse means all tests use this fixture
# session scope means it is only called once
# so this fixture runs once before any tests
def tests_init() -> None:
    # opencv-python installs its own qt version and sets env vars accordingly
    # we remove these to avoid pyqt picking up their XCB QPA plugin & crashing
    for k, v in os.environ.items():
        if k.startswith("QT_") and "cv2" in v:
            del os.environ[k]
    # ensure psychopy has initialized the qt app
    ensureQtApp()
    # work around for PsychHID-WARNING about X11 not being initialized on linux
    if sys.platform == "linux":
        import ctypes

        xlib = ctypes.cdll.LoadLibrary("libX11.so")
        xlib.XInitThreads()
    # if FAILSAFE is True, pyautogui raises an exception
    # if the cursor is in the top-left corner:
    # https://pyautogui.readthedocs.io/en/latest/quickstart.html#fail-safes
    pyautogui.FAILSAFE = False


# fixture to create a Window for testing gui functions
# GLFW backend used for tests as it works better with Xvfb
@pytest.fixture(scope="session")
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


def noise(scale: float = 0.02) -> float:
    return scale * (np.random.random_sample() - 0.1)


def make_mouse_positions(
    pos: Tuple[float, float], time_points: np.ndarray
) -> np.ndarray:
    return np.array([(pos[0] * t + noise(), pos[1] * t + noise()) for t in time_points])


def make_timestamps(n_min: int = 8, n_max: int = 20) -> np.ndarray:
    return np.linspace(0.0, 1.0, np.random.randint(n_min, n_max))


@pytest.fixture
def experiment_no_results() -> MotorTaskExperiment:
    experiment = MotorTaskExperiment()
    trial0 = default_trial()
    trial0["num_targets"] = 4
    trial0["play_sound"] = False
    trial0["target_duration"] = 30.0
    trial0["inter_target_duration"] = 0.0
    trial0["post_block_display_results"] = False
    trial1 = copy.deepcopy(trial0)
    trial1["weight"] = 2
    trial1["num_targets"] = 3
    experiment.trial_list = [trial0, trial1]
    experiment.metadata["name"] = "Experiment with no results"
    experiment.metadata["author"] = "experiment_no_results @pytest.fixture"
    experiment.metadata["date"] = "1666"
    experiment.display_options["to_target_rmse"] = False
    experiment.display_options["averages"] = False
    return experiment


@pytest.fixture
def experiment_with_results() -> MotorTaskExperiment:
    experiment = MotorTaskExperiment()
    # trial without auto-move to center, 3 reps, 8 targets
    trial0 = default_trial()
    # disable sounds due to issues with sounds within tests on linux
    trial0["play_sound"] = False
    trial0["weight"] = 3
    trial0["automove_cursor_to_center"] = False
    # trial with automove to center, 1 rep, 4 targets
    trial1 = default_trial()
    trial0["play_sound"] = False
    trial1["weight"] = 1
    trial1["num_targets"] = 4
    trial1["automove_cursor_to_center"] = True
    experiment.trial_list = [trial0, trial1]
    experiment.metadata["name"] = "Experiment with results"
    experiment.metadata["author"] = "experiment_with_results @pytest.fixture"
    experiment.metadata["date"] = "2000"
    experiment.display_options["to_target_rmse"] = False
    experiment.display_options["averages"] = False
    trial_handler = experiment.create_trialhandler()
    for trial in trial_handler:
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
            if not trial["automove_cursor_to_center"]:
                to_center_timestamps.append(make_timestamps())
                to_center_mouse_positions.append(
                    list(reversed(make_mouse_positions(pos, to_center_timestamps[-1])))
                )
        trial_handler.addData("target_pos", np.array(target_pos))
        trial_handler.addData("to_target_timestamps", np.array(to_target_timestamps))
        trial_handler.addData(
            "to_target_mouse_positions", np.array(to_target_mouse_positions)
        )
        trial_handler.addData("to_center_timestamps", np.array(to_center_timestamps))
        trial_handler.addData(
            "to_center_mouse_positions", np.array(to_center_mouse_positions)
        )
    experiment.trial_handler_with_results = trial_handler
    experiment.has_unsaved_changes = True
    return experiment
