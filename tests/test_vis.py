import multiprocessing
from time import sleep
from typing import Dict
from typing import List
from typing import Tuple

import ascii_magic
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
    nElements = args["n_circles"] + 1
    assert targets.nElements == nElements
    # shape of sizes is x,y pair for each element
    assert targets.sizes.shape == (nElements, 2)
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


def test_display_results(fake_trial: TrialHandlerExt) -> None:
    # pyglet is not threadsafe so GUI code must run in separate process
    # (if threading is used instead get a variety of strange errors)
    process = multiprocessing.Process(
        target=mtpvis.display_results, name="display_results", args=(fake_trial,)
    )
    process.start()
    # wait for display_results screen to be ready
    sleep(2)
    ascii_magic.to_terminal(
        ascii_magic.from_image(pyautogui.screenshot("display_results.png"))
    )
    # press escape to exit
    pyautogui.typewrite(["escape"])
    process.join()
