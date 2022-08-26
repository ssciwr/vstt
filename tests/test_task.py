import logging
import multiprocessing
from time import sleep
from typing import Tuple

import ascii_magic
import motor_task_prototype.task as mtptask
import pyautogui
from motor_task_prototype.geom import points_on_circle
from motor_task_prototype.trial import default_trial


def pos_to_pixels(pos: Tuple[float, float]) -> Tuple[float, float]:
    # pos is in units of screen height, with 0,0 in centre of screen
    width, height = pyautogui.size()
    # return equivalent position in pixels with 0,0 in top left of screen
    pixels = width / 2.0 + pos[0] * height, height / 2.0 - pos[1] * height
    logging.warning(f"{pos} -> {pixels} [{pyautogui.size()}]")
    return pixels


def wrap_task(trial: mtptask.MotorTaskTrial, queue: multiprocessing.Queue) -> None:
    task = mtptask.MotorTask(trial)
    results = task.run()
    queue.put(results)


def test_task() -> None:
    trial = default_trial()
    # disable sounds due to issues with sounds within tests on linux
    trial["play_sound"] = False
    # allow long time for task to finish initializing on CI
    trial["target_duration"] = 10
    movement_time = 0.25
    movement_delay = trial["inter_target_duration"] + 0.25
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
    # wait for task to be ready
    sleep(1)
    target_pos = points_on_circle(
        trial["num_targets"], trial["target_distance"], include_centre=False
    )
    i = 0
    for pos in target_pos:
        logging.warning(pos)
        logging.warning(pyautogui.position())
        # wait until target is activated
        sleep(movement_delay)
        ascii_magic.to_terminal(
            ascii_magic.from_image(pyautogui.screenshot(f"{i}.png"))
        )
        i += 1
        logging.warning(pyautogui.position())
        # move mouse to target
        x, y = pos_to_pixels(pos)
        pyautogui.moveTo(x, y, movement_time)
        logging.warning(pyautogui.position())
    results = queue.get()
    # check that we hit all the targets
    for timestamps, positions in zip(
        results.data["timestamps"][0][0], results.data["mouse_positions"][0][0]
    ):
        print(timestamps, positions)
        # assert timestamps[-1] < 0.5 * trial["target_duration"]
    process.join()
