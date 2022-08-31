import multiprocessing
from time import sleep
from typing import List
from typing import Tuple

import ascii_magic
import motor_task_prototype.task as mtptask
import numpy as np
import pyautogui
from motor_task_prototype.geom import points_on_circle
from motor_task_prototype.trial import default_trial
from psychopy.data import TrialHandlerExt


def ascii_screenshot() -> None:
    print(f"\n{ascii_magic.from_image(pyautogui.screenshot())}\n")


# return true if pixel or any neighbours is of the desired color
def pixel_color(pixel: Tuple[float, float], color: Tuple[int, int, int]) -> bool:
    img = pyautogui.screenshot().load()
    for dx in [0, 1, -1]:
        for dy in [0, 1, -1]:
            p = (pixel[0] + dx, pixel[1] + dy)
            if np.allclose(img[p], color):
                return True
    return False


def pos_to_pixels(pos: Tuple[float, float]) -> Tuple[float, float]:
    # pos is in units of screen height, with 0,0 in centre of screen
    width, height = pyautogui.size()
    # return equivalent position in pixels with 0,0 in top left of screen
    pixels = width / 2.0 + pos[0] * height, height / 2.0 - pos[1] * height
    return pixels


def wrap_task(trial: mtptask.MotorTaskTrial, queue: multiprocessing.Queue) -> None:
    task = mtptask.MotorTask(trial)
    results = task.run(win_type="glfw")
    queue.put(results)


def move_mouse_to_target(
    target_pixel: Tuple[float, float],
    target_color: Tuple[int, int, int] = (255, 0, 0),
    movement_time: float = 0.2,
) -> None:
    # wait until target is activated
    while not pixel_color(target_pixel, target_color):
        sleep(0.1)
    # ascii image of screen for debugging logs
    ascii_screenshot()
    # move mouse to target
    pyautogui.moveTo(target_pixel[0], target_pixel[1], movement_time)


def do_task(
    trial: mtptask.MotorTaskTrial, target_pixels: List[Tuple[float, float]]
) -> TrialHandlerExt:
    queue: multiprocessing.Queue = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=wrap_task,
        name="task",
        args=(
            trial,
            queue,
        ),
    )
    process.start()
    for target_pixel in target_pixels:
        move_mouse_to_target(target_pixel)
    results = queue.get()
    process.join()
    return results


def test_task() -> None:
    trial = default_trial()
    # disable sounds due to issues with sounds within tests on linux
    trial["play_sound"] = False
    target_pixels = [
        pos_to_pixels(pos)
        for pos in points_on_circle(
            trial["num_targets"], trial["target_distance"], include_centre=False
        )
    ]
    results = do_task(trial, target_pixels)
    # check that we hit all the targets without timing out
    for timestamps in results.data["timestamps"][0][0]:
        assert timestamps[-1] < 0.5 * trial["target_duration"]


def test_task_no_automove_to_center() -> None:
    trial = default_trial()
    # disable sounds due to issues with sounds within tests on linux
    trial["play_sound"] = False
    trial["automove_cursor_to_center"] = False
    target_pixels = []
    for pos in points_on_circle(
        trial["num_targets"], trial["target_distance"], include_centre=False
    ):
        # after moving to each target need to return mouse to central target
        target_pixels.append(pos_to_pixels(pos))
        target_pixels.append(pos_to_pixels((0, 0)))
    results = do_task(trial, target_pixels)
    # check that we hit all the targets
    for timestamps, timestamps_back in zip(
        results.data["timestamps"][0][0], results.data["timestamps_back"][0][0]
    ):
        assert timestamps[-1] < 0.5 * trial["target_duration"]
        assert timestamps_back[-1] < 0.5 * trial["target_duration"]
