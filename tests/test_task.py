import multiprocessing
from time import sleep
from typing import Tuple

import ascii_magic
import motor_task_prototype.task as mtptask
import numpy as np
import pyautogui
from motor_task_prototype.geom import points_on_circle
from motor_task_prototype.trial import default_trial


def ascii_screenshot() -> None:
    print(f"\n{ascii_magic.from_image(pyautogui.screenshot())}\n")


def pixel_color(pixel: Tuple[float, float], color: Tuple[int, int, int]) -> bool:
    return np.allclose(pyautogui.screenshot().load()[pixel], color)


def pos_to_pixels(pos: Tuple[float, float]) -> Tuple[float, float]:
    # pos is in units of screen height, with 0,0 in centre of screen
    width, height = pyautogui.size()
    # return equivalent position in pixels with 0,0 in top left of screen
    pixels = width / 2.0 + pos[0] * height, height / 2.0 - pos[1] * height
    return pixels


def wrap_task(trial: mtptask.MotorTaskTrial, queue: multiprocessing.Queue) -> None:
    task = mtptask.MotorTask(trial)
    results = task.run(winType="glfw")
    queue.put(results)


def test_task() -> None:
    trial = default_trial()
    # disable sounds due to issues with sounds within tests on linux
    trial["play_sound"] = False
    movement_time = 0.5
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
    target_pixels = [
        pos_to_pixels(pos)
        for pos in points_on_circle(
            trial["num_targets"], trial["target_distance"], include_centre=False
        )
    ]
    for pixel in target_pixels:
        # wait until target is activated
        while not pixel_color(pixel, (255, 0, 0)):
            sleep(0.1)
        ascii_screenshot()
        # move mouse to target
        pyautogui.moveTo(pixel[0], pixel[1], movement_time)
    results = queue.get()
    # check that we hit all the targets
    for timestamps, positions in zip(
        results.data["timestamps"][0][0], results.data["mouse_positions"][0][0]
    ):
        assert timestamps[-1] < 0.5 * trial["target_duration"]
    process.join()
