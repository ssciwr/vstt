import threading
from time import sleep
from typing import List
from typing import Tuple

import gui_test_utils as gtu
import motor_task_prototype.task as mtptask
import pyautogui
from motor_task_prototype.geom import points_on_circle
from psychopy.data import TrialHandlerExt
from psychopy.visual.window import Window


def move_mouse_to_target(
    target_pixel: Tuple[float, float],
    target_color: Tuple[int, int, int] = (255, 0, 0),
    movement_time: float = 0.2,
) -> None:
    # wait until target is activated
    attempts = 0
    while not gtu.pixel_color(target_pixel, target_color):
        sleep(0.2)
        # press Enter in case we are looking at a splash / display_results screen
        gtu.press_enter()
        attempts += 1
        if attempts > 10:
            print(f"Stuck waiting for target at {target_pixel} to activate", flush=True)
            gtu.ascii_screenshot()
    gtu.ascii_screenshot()
    # move mouse to target
    pyautogui.moveTo(target_pixel[0], target_pixel[1], movement_time)


def do_task(
    experiment: TrialHandlerExt, target_pixels: List[List[Tuple[float, float]]]
) -> None:
    gtu.ascii_screenshot()
    for target_pixels_block, trial in zip(target_pixels, experiment.trialList):
        for rep in range(trial["weight"]):
            for target_pixel in target_pixels_block:
                move_mouse_to_target(target_pixel)


def launch_do_task(
    experiment: TrialHandlerExt, target_pixels: List[List[Tuple[float, float]]]
) -> threading.Thread:
    thread = threading.Thread(
        target=do_task,
        name="task",
        args=(
            experiment,
            target_pixels,
        ),
    )
    thread.start()
    return thread


def test_task(experiment_no_results: TrialHandlerExt, window: Window) -> None:
    target_pixels = []
    for trial in experiment_no_results.trialList:
        trial["automove_cursor_to_center"] = True
        target_pixels.append(
            [
                gtu.pos_to_pixels(pos)
                for pos in points_on_circle(
                    trial["num_targets"],
                    trial["target_distance"],
                    include_centre=False,
                )
            ]
        )
    do_task_thread = launch_do_task(experiment_no_results, target_pixels)
    task = mtptask.MotorTask(experiment_no_results)
    results = task.run(window)
    do_task_thread.join()
    # check that we hit all the targets without timing out
    for timestamps in results.data["to_target_timestamps"][0][0]:
        assert (
            timestamps[-1] < 0.5 * experiment_no_results.trialList[0]["target_duration"]
        )


def test_task_no_automove_to_center(
    experiment_no_results: TrialHandlerExt, window: Window
) -> None:
    target_pixels = []
    for trial in experiment_no_results.trialList:
        trial["automove_cursor_to_center"] = False
        tp = []
        for pos in points_on_circle(
            trial["num_targets"],
            trial["target_distance"],
            include_centre=False,
        ):
            # after moving to each target need to return mouse to central target
            tp.append(gtu.pos_to_pixels(pos))
            tp.append(gtu.pos_to_pixels((0, 0)))
        target_pixels.append(tp)
    do_task_thread = launch_do_task(experiment_no_results, target_pixels)
    task = mtptask.MotorTask(experiment_no_results)
    results = task.run(window)
    do_task_thread.join()
    # check that we hit all the targets
    for to_target_timestamps, to_center_timestamps in zip(
        results.data["to_target_timestamps"][0][0],
        results.data["to_center_timestamps"][0][0],
    ):
        assert (
            to_target_timestamps[-1]
            < 0.5 * experiment_no_results.trialList[0]["target_duration"]
        )
        assert (
            to_center_timestamps[-1]
            < 0.5 * experiment_no_results.trialList[0]["target_duration"]
        )
