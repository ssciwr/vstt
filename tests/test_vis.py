import threading
from time import sleep
from typing import Dict
from typing import List
from typing import Tuple

import motor_task_prototype.vis as mtpvis
import numpy as np
import pyautogui
import pytest
from psychopy.data import TrialHandlerExt
from psychopy.visual.window import Window


def test_make_cursor(window: Window) -> None:
    cursor = mtpvis.make_cursor(window)
    assert np.allclose(cursor.pos, [0, 0])


@pytest.mark.parametrize(
    "args,xys",
    [
        (
            {
                "n_circles": 1,
                "radius": 0.5,
                "point_radius": 0.1,
                "center_point_radius": 0.05,
            },
            [(0, 0.5), (0, 0)],
        ),
        (
            {
                "n_circles": 2,
                "radius": 0.3,
                "point_radius": 0.02,
                "center_point_radius": 0.04,
            },
            [(0, 0.3), (0, -0.3), (0, 0)],
        ),
        (
            {
                "n_circles": 4,
                "radius": 0.8,
                "point_radius": 0.2,
                "center_point_radius": 0.07,
            },
            [(0, 0.8), (0.8, 0), (0, -0.8), (-0.8, 0), (0, 0)],
        ),
    ],
)
def test_make_targets(
    window: Window, args: Dict, xys: List[Tuple[float, float]]
) -> None:
    targets = mtpvis.make_targets(window, **args)
    n_elem = args["n_circles"] + 1
    assert targets.nElements == n_elem
    # shape of sizes is x,y pair for each element
    assert targets.sizes.shape == (n_elem, 2)
    # size is circumference of circle in both x and y directions
    point_size = 2 * args["point_radius"]
    for size in targets.sizes[0:-1]:
        assert np.allclose(size, [point_size, point_size])
    center_point_size = 2 * args["center_point_radius"]
    assert np.allclose(targets.sizes[-1], [center_point_size, center_point_size])
    assert np.allclose(targets.xys, xys)


@pytest.mark.parametrize("n_targets", [1])
def test_update_target_colors(window: Window, n_targets: int) -> None:
    grey = (0.1, 0.1, 0.1)
    red = (1.0, -1.0, -1.0)
    targets = mtpvis.make_targets(window, n_targets, 0.5, 0.05, 0.05)
    n_elem = n_targets + 1
    # calling without specifying an index makes all elements grey
    mtpvis.update_target_colors(targets)
    assert targets.colors.shape == (n_elem, 3)
    for color in targets.colors:
        assert np.allclose(color, grey)
    # calling with index makes that element red, the rest grey
    for index in range(n_elem):
        mtpvis.update_target_colors(targets, index=index)
        assert targets.colors.shape == (n_elem, 3)
        for i in range(n_elem):
            if i == index:
                assert np.allclose(targets.colors[i], red)
            else:
                assert np.allclose(targets.colors[i], grey)


def rms_diff(a: np.ndarray, b: np.ndarray) -> float:
    return np.sqrt(np.mean(np.square(a - b)))


def get_display_screenshot_when_ready(
    screenshot_before: np.ndarray,
    min_rms_diff: float = 0.1,
    delay_between_screenshots: float = 0.1,
) -> np.ndarray:
    s0 = np.asarray(screenshot_before)
    sleep(delay_between_screenshots)
    s = np.asarray(pyautogui.screenshot())
    # wait until
    #   - screen differs significantly from original screenshot
    #   - is not all black (xvfb initial screen)
    #   - is not all grey (psychopy initial screen)
    while rms_diff(s, s0) < min_rms_diff or np.mean(s) in [0.0, 128.0]:
        sleep(delay_between_screenshots)
        s = np.asarray(pyautogui.screenshot())
    return s


def show_display(
    experiment: TrialHandlerExt,
    trial_indices: List[int],
) -> np.ndarray:
    # GLFW backend used for tests as it works better with Xvfb
    process = threading.Thread(
        target=mtpvis.display_results,
        name="display_results",
        args=(experiment, trial_indices, None, "glfw"),
    )
    screenshot_before = pyautogui.screenshot()
    process.start()
    screenshot = get_display_screenshot_when_ready(screenshot_before)
    # press escape to exit
    pyautogui.typewrite(["escape"])
    process.join()
    return screenshot


def pixel_color_fraction(img: np.ndarray, color: Tuple[int, int, int]) -> float:
    return np.count_nonzero((img == np.array(color)).all(axis=2)) / (img.size / 3)


def test_display_results_nothing(experiment_with_results: TrialHandlerExt) -> None:
    experiment_with_results.extraInfo["display_options"] = {
        "to_target_paths": False,
        "to_center_paths": False,
        "targets": False,
        "central_target": False,
        "to_target_reaction_time": False,
        "to_center_reaction_time": False,
        "to_target_time": False,
        "to_center_time": False,
        "to_target_distance": False,
        "to_center_distance": False,
        "to_target_rmse": False,
        "to_center_rmse": False,
        "averages": False,
    }
    trial_indices = [0, 1, 2]
    screenshot = show_display(experiment_with_results, trial_indices)
    # all pixels grey except for blue continue text
    assert 0.990 < pixel_color_fraction(screenshot, (128, 128, 128)) < 0.999
    # no off-white pixels
    assert pixel_color_fraction(screenshot, (240, 248, 255)) == 0.000


def test_display_results_everything(experiment_with_results: TrialHandlerExt) -> None:
    experiment_with_results.extraInfo["display_options"] = {
        "to_target_paths": True,
        "to_center_paths": True,
        "targets": True,
        "central_target": True,
        "to_target_reaction_time": True,
        "to_center_reaction_time": True,
        "to_target_time": True,
        "to_center_time": True,
        "to_target_distance": True,
        "to_center_distance": True,
        "to_target_rmse": True,
        "to_center_rmse": True,
        "averages": True,
    }
    trial_indices = [0, 1, 2]
    screenshot = show_display(experiment_with_results, trial_indices)
    # less grey: lots of other colors for targets, paths and stats
    assert 0.750 < pixel_color_fraction(screenshot, (128, 128, 128)) < 0.950
    # some off-white pixels for one of the targets
    assert 0.002 < pixel_color_fraction(screenshot, (240, 248, 255)) < 0.100
