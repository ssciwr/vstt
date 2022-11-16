from __future__ import annotations

from typing import Dict
from typing import List
from typing import Tuple

import gui_test_utils as gtu
import motor_task_prototype.meta as mtpmeta
import motor_task_prototype.vis as mtpvis
import numpy as np
import pytest
from motor_task_prototype.experiment import MotorTaskExperiment
from psychopy.visual.window import Window


def test_make_cursor(window: Window) -> None:
    for cursor_size in [0.01, 0.02235457]:
        cursor = mtpvis.make_cursor(window, cursor_size)
        assert np.allclose(cursor.pos, [0, 0])
        # x size:
        assert np.allclose(cursor.vertices[1][0] - cursor.vertices[0][0], cursor_size)
        # y size:
        assert np.allclose(cursor.vertices[-1][1] - cursor.vertices[-2][1], cursor_size)


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
    for show_inactive_targets, inactive_color in [
        (True, (0.1, 0.1, 0.1)),
        (False, (0, 0, 0)),
    ]:
        red = (1.0, -1.0, -1.0)
        targets = mtpvis.make_targets(window, n_targets, 0.5, 0.05, 0.05)
        n_elem = n_targets + 1
        # calling without specifying an index makes all elements grey
        mtpvis.update_target_colors(
            targets, show_inactive_targets=show_inactive_targets
        )
        assert targets.colors.shape == (n_elem, 3)
        for color in targets.colors:
            assert np.allclose(color, inactive_color)
        # calling with index makes that element red, the rest grey
        for index in range(n_elem):
            mtpvis.update_target_colors(
                targets, show_inactive_targets=show_inactive_targets, index=index
            )
            assert targets.colors.shape == (n_elem, 3)
            for i in range(n_elem):
                if i == index:
                    assert np.allclose(targets.colors[i], red)
                else:
                    assert np.allclose(targets.colors[i], inactive_color)


def test_splash_screen_defaults(window: Window) -> None:
    metadata = mtpmeta.default_metadata()
    screenshot = gtu.call_target_and_get_screenshot(
        mtpvis.splash_screen, (metadata, window), window
    )
    # most pixels grey except for black main text and blue continue text
    assert 0.900 < gtu.pixel_color_fraction(screenshot, (128, 128, 128)) < 0.999
    # some black pixels
    assert 0.000 < gtu.pixel_color_fraction(screenshot, (0, 0, 0)) < 0.100
    # no white pixels
    assert gtu.pixel_color_fraction(screenshot, (255, 255, 255)) == 0.000


def test_display_results_nothing(
    experiment_with_results: MotorTaskExperiment, window: Window
) -> None:
    experiment_with_results.display_options = {
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
    # trial data without auto-move to center
    trial_indices = [0, 1, 2]
    screenshot = gtu.call_target_and_get_screenshot(
        mtpvis.display_results,
        (
            experiment_with_results.trial_handler_with_results,
            experiment_with_results.display_options,
            trial_indices,
            window,
        ),
        window,
    )
    # all pixels grey except for blue continue text
    assert 0.990 < gtu.pixel_color_fraction(screenshot, (128, 128, 128)) < 0.999
    # no off-white pixels
    assert gtu.pixel_color_fraction(screenshot, (240, 248, 255)) == 0.000
    # trial data with auto-move to center
    trial_indices = [3]
    screenshot = gtu.call_target_and_get_screenshot(
        mtpvis.display_results,
        (
            experiment_with_results.trial_handler_with_results,
            experiment_with_results.display_options,
            trial_indices,
            window,
        ),
        window,
    )
    # all pixels grey except for blue continue text
    assert 0.990 < gtu.pixel_color_fraction(screenshot, (128, 128, 128)) < 0.999
    # no off-white pixels
    assert gtu.pixel_color_fraction(screenshot, (240, 248, 255)) == 0.000


def test_display_results_everything(
    experiment_with_results: MotorTaskExperiment, window: Window
) -> None:
    experiment_with_results.display_options = {
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
    # trial data without auto-move to center
    trial_indices = [0, 1, 2]
    screenshot = gtu.call_target_and_get_screenshot(
        mtpvis.display_results,
        (
            experiment_with_results.trial_handler_with_results,
            experiment_with_results.display_options,
            trial_indices,
            window,
        ),
        window,
    )
    # less grey: lots of other colors for targets, paths and stats
    grey_pixels = gtu.pixel_color_fraction(screenshot, (128, 128, 128))
    assert 0.750 < grey_pixels < 0.950
    # some off-white pixels for one of the targets
    off_white_pixels = gtu.pixel_color_fraction(screenshot, (240, 248, 255))
    assert 0.002 < off_white_pixels < 0.100
    # trial data with auto-move to center
    trial_indices = [3]
    screenshot = gtu.call_target_and_get_screenshot(
        mtpvis.display_results,
        (
            experiment_with_results.trial_handler_with_results,
            experiment_with_results.display_options,
            trial_indices,
            window,
        ),
        window,
    )
    # more grey since there are fewer paths and stats to display
    assert gtu.pixel_color_fraction(screenshot, (128, 128, 128)) > grey_pixels
