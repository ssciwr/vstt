from __future__ import annotations

import gui_test_utils as gtu
import numpy as np
import pytest
from psychopy.visual.window import Window
from pytest import approx

import vstt
from vstt.experiment import Experiment


def test_make_cursor(window: Window) -> None:
    for cursor_size in [0.01, 0.02235457]:
        cursor = vstt.vis.make_cursor(window, cursor_size)
        assert np.allclose(cursor.pos, [0, 0])
        # x size:
        assert np.allclose(cursor.vertices[1][0] - cursor.vertices[0][0], cursor_size)
        # y size:
        assert np.allclose(cursor.vertices[-1][1] - cursor.vertices[-2][1], cursor_size)


@pytest.mark.parametrize("add_central_target", [True, False])
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
    window: Window, args: dict, xys: list[tuple[float, float]], add_central_target: bool
) -> None:
    args["add_central_target"] = add_central_target
    targets = vstt.vis.make_targets(window, **args)
    n_elem = args["n_circles"] + (1 if add_central_target else 0)
    assert targets.nElements == n_elem
    # shape of sizes is x,y pair for each element
    assert targets.sizes.shape == (n_elem, 2)
    # size is circumference of circle in both x and y directions
    point_size = 2 * args["point_radius"]
    for size in targets.sizes[: args["n_circles"]]:
        assert np.allclose(size, [point_size, point_size])
    if add_central_target:
        center_point_size = 2 * args["center_point_radius"]
        assert np.allclose(targets.sizes[-1], [center_point_size, center_point_size])
    assert np.allclose(targets.xys, xys[0:n_elem])


@pytest.mark.parametrize("add_central_target", [True, False])
@pytest.mark.parametrize("n_targets", [1, 2, 3, 5, 12])
def test_update_target_colors(
    window: Window, n_targets: int, add_central_target: bool
) -> None:
    for show_inactive_targets, inactive_color in [
        (True, (0.9, 0.9, 0.9)),
        (False, (0, 0, 0)),
    ]:
        red = (1.0, -1.0, -1.0)
        targets = vstt.vis.make_targets(
            window, n_targets, 0.5, 0.05, add_central_target, 0.05
        )
        n_elem = n_targets + (1 if add_central_target else 0)
        # calling without specifying an index makes all elements grey
        vstt.vis.update_target_colors(
            targets, show_inactive_targets=show_inactive_targets
        )
        if n_elem == 1:
            # apparently psychopy collapses (n_elem,3) shape to (3) for n_elem=1 case:
            assert targets.colors.shape == (3,)
        else:
            assert targets.colors.shape == (n_elem, 3)
        for color in targets.colors:
            assert np.allclose(color, inactive_color)
        # calling with index makes that element red, the rest grey
        for index in range(n_elem):
            vstt.vis.update_target_colors(
                targets, show_inactive_targets=show_inactive_targets, index=index
            )
            if n_elem == 1:
                # apparently psychopy collapses (n_elem,3) shape to (3) for n_elem=1 case:
                assert targets.colors.shape == (3,)
            else:
                assert targets.colors.shape == (n_elem, 3)
            for i in range(n_elem):
                if i == index:
                    if n_elem == 1:
                        # apparently psychopy collapses (n_elem,3) shape to (3) for n_elem=1 case:
                        assert np.allclose(targets.colors, red)
                    else:
                        assert np.allclose(targets.colors[i], red)
                else:
                    assert np.allclose(targets.colors[i], inactive_color)


@pytest.mark.parametrize(
    "args,xys",
    [
        (
            {
                "n_circles": 1,
                "radius": 0.44,
                "point_radius": 0.1,
            },
            [(0, 0.44)],
        ),
        (
            {
                "n_circles": 4,
                "radius": 0.3,
                "point_radius": 0.05,
            },
            [(0, 0.3), (0.3, 0), (0, -0.3), (-0.3, 0)],
        ),
    ],
)
def test_make_target_labels(
    window: Window, args: dict, xys: list[tuple[float, float]]
) -> None:
    # more labels than targets: label each target and ignore any extra labels
    args["labels_string"] = "a b c d e f"
    label_strings = ["a", "b", "c", "d", "e", "f"]
    target_labels = vstt.vis.make_target_labels(window, **args)
    assert len(target_labels) == args["n_circles"]
    for target_label, label_string, xy in zip(target_labels, label_strings, xys):
        assert target_label.text == label_string
        assert target_label.letterHeight < 2 * args["point_radius"]
        assert np.allclose(target_label.pos, xy)
    # equal or fewer labels than targets: just use available labels
    args["labels_string"] = "10"
    label_strings = ["10"]
    target_labels = vstt.vis.make_target_labels(window, **args)
    assert len(target_labels) == 1
    for target_label, label_string, xy in zip(target_labels, label_strings, xys):
        assert target_label.text == label_string
        assert target_label.letterHeight < 2 * args["point_radius"]
        assert np.allclose(target_label.pos, xy)


@pytest.mark.parametrize("n_targets", [1, 2, 3, 5, 12])
def test_update_target_label_colors(window: Window, n_targets: int) -> None:
    labels = "a b c d e f g h i j k l m n o p"
    for show_inactive_targets, inactive_color in [
        (True, (0.3, 0.3, 0.3)),
        (False, (0, 0, 0)),
    ]:
        white = (1.0, 1.0, 1.0)
        target_labels = vstt.vis.make_target_labels(
            window, n_targets, 0.5, 0.05, labels
        )
        # calling without specifying an index makes all elements grey
        vstt.vis.update_target_label_colors(
            target_labels, show_inactive_targets=show_inactive_targets
        )
        assert len(target_labels) == n_targets
        for target_label in target_labels:
            assert np.allclose(target_label.color, inactive_color)
        # calling with index makes that element red, the rest grey
        for index in range(n_targets):
            vstt.vis.update_target_label_colors(
                target_labels, show_inactive_targets=show_inactive_targets, index=index
            )
            assert len(target_labels) == n_targets
            for i, target_label in enumerate(target_labels):
                if i == index:
                    assert np.allclose(target_label.color, white)
                else:
                    assert np.allclose(target_label.color, inactive_color)


def test_splash_screen_defaults(window: Window) -> None:
    metadata = vstt.meta.default_metadata()
    screenshot = gtu.call_target_and_get_screenshot(
        vstt.vis.splash_screen, (1000, True, False, metadata, window), window
    )
    # most pixels grey except for black main text and blue continue text
    assert 0.900 < gtu.pixel_color_fraction(screenshot, (128, 128, 128)) < 0.999
    # some black pixels
    assert 0.000 < gtu.pixel_color_fraction(screenshot, (0, 0, 0)) < 0.100
    # no white pixels
    assert gtu.pixel_color_fraction(screenshot, (255, 255, 255)) == approx(0)


def test_display_results_nothing(
    experiment_with_results: Experiment, window: Window
) -> None:
    experiment_with_results.display_options = {
        "to_target_paths": False,
        "to_center_paths": False,
        "targets": False,
        "central_target": False,
        "to_target_reaction_time": False,
        "to_center_reaction_time": False,
        "to_target_movement_time": False,
        "to_center_movement_time": False,
        "to_target_time": False,
        "to_center_time": False,
        "to_target_distance": False,
        "to_center_distance": False,
        "to_target_rmse": False,
        "to_center_rmse": False,
        "averages": False,
        "to_target_success": False,
        "to_center_success": False,
        "area": False,
        "normalized_area": False,
        "peak_velocity": False,
        "peak_acceleration": False,
        "to_target_spatial_error": False,
        "to_center_spatial_error": False,
        "movement_time_at_peak_velocity": False,
        "total_time_at_peak_velocity": False,
        "movement_distance_at_peak_velocity": False,
        "rmse_movement_at_peak_velocity": False,
    }
    for all_trials_for_this_condition in [False, True]:
        # trial 0: 0,1,2 are trials without auto-move to center
        screenshot = gtu.call_target_and_get_screenshot(
            vstt.vis.display_results,
            (
                60,
                True,
                False,
                experiment_with_results.trial_handler_with_results,
                experiment_with_results.display_options,
                0,
                all_trials_for_this_condition,
                window,
            ),
            window,
        )
        # all pixels grey except for blue continue text
        assert 0.990 < gtu.pixel_color_fraction(screenshot, (128, 128, 128)) < 0.999
        # no off-white pixels
        assert gtu.pixel_color_fraction(screenshot, (240, 248, 255)) == approx(0)
        # trial 3: with auto-move to center
        screenshot = gtu.call_target_and_get_screenshot(
            vstt.vis.display_results,
            (
                60,
                True,
                False,
                experiment_with_results.trial_handler_with_results,
                experiment_with_results.display_options,
                3,
                all_trials_for_this_condition,
                window,
            ),
            window,
        )
        # all pixels grey except for blue continue text
        assert 0.990 < gtu.pixel_color_fraction(screenshot, (128, 128, 128)) < 0.999
        # no off-white pixels
        assert gtu.pixel_color_fraction(screenshot, (240, 248, 255)) == approx(0)


def test_display_results_everything(
    experiment_with_results: Experiment, window: Window
) -> None:
    experiment_with_results.display_options = {
        "to_target_paths": True,
        "to_center_paths": True,
        "targets": True,
        "central_target": True,
        "to_target_reaction_time": True,
        "to_center_reaction_time": True,
        "to_target_movement_time": True,
        "to_center_movement_time": True,
        "to_target_time": True,
        "to_center_time": True,
        "to_target_distance": True,
        "to_center_distance": True,
        "to_target_rmse": True,
        "to_center_rmse": True,
        "averages": True,
        "to_target_success": True,
        "to_center_success": True,
        "area": True,
        "normalized_area": True,
        "peak_velocity": True,
        "peak_acceleration": True,
        "to_target_spatial_error": True,
        "to_center_spatial_error": True,
        "movement_time_at_peak_velocity": True,
        "total_time_at_peak_velocity": True,
        "movement_distance_at_peak_velocity": True,
        "rmse_movement_at_peak_velocity": True,
    }
    for all_trials_for_this_condition in [False, True]:
        # trial 0: 0,1,2 are trials without auto-move to center
        screenshot = gtu.call_target_and_get_screenshot(
            vstt.vis.display_results,
            (
                60,
                True,
                False,
                experiment_with_results.trial_handler_with_results,
                experiment_with_results.display_options,
                0,
                all_trials_for_this_condition,
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
        # trial 3: with auto-move to center
        screenshot = gtu.call_target_and_get_screenshot(
            vstt.vis.display_results,
            (
                60,
                True,
                False,
                experiment_with_results.trial_handler_with_results,
                experiment_with_results.display_options,
                3,
                all_trials_for_this_condition,
                window,
            ),
            window,
        )
        # more grey since there are fewer paths and stats to display
        assert gtu.pixel_color_fraction(screenshot, (128, 128, 128)) > grey_pixels
