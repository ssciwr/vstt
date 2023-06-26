from __future__ import annotations

import copy
import os
import sys
from typing import Tuple

import numpy as np
import pyautogui
import pytest
from psychopy.gui.qtgui import ensureQtApp
from psychopy.visual.window import Window
from vstt.experiment import Experiment
from vstt.geom import points_on_circle
from vstt.stats import stats_dataframe
from vstt.trial import default_trial

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
    # work around for PsychHID-WARNING about X11 not being initialized on linux:
    if sys.platform == "linux":
        import ctypes

        xlib = ctypes.cdll.LoadLibrary("libX11.so")
        xlib.XInitThreads()
    # if FAILSAFE is True, pyautogui raises an exception
    # if the cursor is in the top-left corner:
    # https://pyautogui.readthedocs.io/en/latest/quickstart.html#fail-safes
    pyautogui.FAILSAFE = False


# fixture to create a Window for testing gui functions
@pytest.fixture(scope="session")
def window() -> Window:
    window = Window(fullscr=True, units="height")
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


def make_timestamps(t0: float, n_min: int = 8, n_max: int = 20) -> np.ndarray:
    return np.linspace(t0, t0 + 1.0, np.random.randint(n_min, n_max))


@pytest.fixture
def experiment_no_results() -> Experiment:
    experiment = Experiment()
    trial0 = default_trial()
    trial0["num_targets"] = 4
    trial0["play_sound"] = False
    trial0["target_duration"] = 60.0
    trial0["central_target_duration"] = 60.0
    trial0["pre_target_delay"] = 0.0
    trial0["pre_central_target_delay"] = 0.0
    trial0["post_block_display_results"] = False
    trial0["post_block_delay"] = 0.1
    trial1 = copy.deepcopy(trial0)
    trial1["weight"] = 2
    trial1["num_targets"] = 3
    trial1["post_block_delay"] = 0.1
    experiment.trial_list = [trial0, trial1]
    experiment.metadata["name"] = "Experiment with no results"
    experiment.metadata["author"] = "experiment_no_results @pytest.fixture"
    experiment.metadata["date"] = "1666"
    experiment.display_options["to_target_rmse"] = False
    experiment.display_options["averages"] = False
    return experiment


@pytest.fixture
def experiment_with_results() -> Experiment:
    experiment = Experiment()
    # trial without auto-move to center, 3 reps, 8 targets
    trial0 = default_trial()
    # disable sounds due to issues with sounds within tests on linux CI
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
        to_target_num_timestamps_before_visible = []
        to_center_timestamps = []
        to_center_num_timestamps_before_visible = []
        to_target_mouse_positions = []
        to_center_mouse_positions = []
        to_target_success = []
        to_center_success = []
        target_pos = points_on_circle(
            trial["num_targets"], trial["target_distance"], include_centre=False
        )
        t0 = 0.0
        for pos in target_pos:
            to_target_timestamps.append(make_timestamps(t0))
            to_target_num_timestamps_before_visible.append(0)
            to_target_mouse_positions.append(
                make_mouse_positions(pos, to_target_timestamps[-1])
            )
            to_target_success.append(True)
            t0 = to_target_timestamps[-1][-1] + 1.0 / 60.0
            if not trial["automove_cursor_to_center"]:
                to_center_timestamps.append(make_timestamps(t0))
                to_center_num_timestamps_before_visible.append(0)
                to_center_mouse_positions.append(
                    list(reversed(make_mouse_positions(pos, to_center_timestamps[-1])))
                )
                to_center_success.append(True)
                t0 = to_center_timestamps[-1][-1] + 1.0 / 60.0
        trial_handler.addData("target_indices", np.array(range(len(target_pos))))
        trial_handler.addData("target_pos", np.array(target_pos))
        trial_handler.addData(
            "to_target_timestamps", np.array(to_target_timestamps, dtype=object)
        )
        trial_handler.addData(
            "to_target_num_timestamps_before_visible",
            np.array(to_target_num_timestamps_before_visible),
        )
        trial_handler.addData(
            "to_target_mouse_positions",
            np.array(to_target_mouse_positions, dtype=object),
        )
        trial_handler.addData("to_target_success", np.array(to_target_success))
        trial_handler.addData(
            "to_center_timestamps", np.array(to_center_timestamps, dtype=object)
        )
        trial_handler.addData(
            "to_center_mouse_positions",
            np.array(to_center_mouse_positions, dtype=object),
        )
        trial_handler.addData(
            "to_center_num_timestamps_before_visible",
            np.array(to_target_num_timestamps_before_visible),
        )
        if trial["automove_cursor_to_center"]:
            to_center_success = [True] * trial["num_targets"]
        trial_handler.addData("to_center_success", np.array(to_center_success))
    experiment.trial_handler_with_results = trial_handler
    experiment.stats = stats_dataframe(trial_handler)
    experiment.has_unsaved_changes = True
    return experiment
