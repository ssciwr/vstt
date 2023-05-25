from __future__ import annotations

import threading
from time import sleep
from typing import List
from typing import Tuple

import gui_test_utils as gtu
import numpy as np
import pyautogui
import vstt
from psychopy.visual.window import Window
from vstt.experiment import Experiment
from vstt.geom import points_on_circle
from vstt.task import MotorTask


def move_mouse_to_target(
    target_pixel: Tuple[float, float],
    target_color: Tuple[int, int, int] = (255, 0, 0),
    movement_time: float = 0.1,
) -> None:
    # wait until target is activated
    attempts = 0
    while not gtu.pixel_color(target_pixel, target_color):
        sleep(0.1)
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
    experiment: Experiment, target_pixels: List[List[Tuple[float, float]]]
) -> None:
    gtu.ascii_screenshot()
    for target_pixels_block, trial in zip(target_pixels, experiment.trial_list):
        for rep in range(trial["weight"]):
            for target_pixel in target_pixels_block:
                move_mouse_to_target(target_pixel)


def launch_do_task(
    experiment: Experiment, target_pixels: List[List[Tuple[float, float]]]
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


def test_task_no_trials(window: Window) -> None:
    experiment_no_trials = Experiment()
    experiment_no_trials.trial_list = []
    experiment_no_trials.has_unsaved_changes = False
    assert experiment_no_trials.trial_handler_with_results is None
    do_task_thread = launch_do_task(experiment_no_trials, [])
    task = MotorTask(experiment_no_trials, window)
    success = task.run()
    do_task_thread.join()
    assert success is False
    assert experiment_no_trials.has_unsaved_changes is False
    assert experiment_no_trials.trial_handler_with_results is None


def test_task_automove_to_center(
    experiment_no_results: Experiment, window: Window
) -> None:
    target_pixels = []
    experiment_no_results.has_unsaved_changes = False
    assert experiment_no_results.trial_handler_with_results is None
    for trial in experiment_no_results.trial_list:
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
    task = MotorTask(experiment_no_results, window)
    success = task.run()
    do_task_thread.join()
    # task ran successfully, updated experiment with results
    assert success is True
    assert experiment_no_results.has_unsaved_changes is True
    assert experiment_no_results.trial_handler_with_results is not None
    # check that we hit all the targets without timing out
    for timestamps in experiment_no_results.trial_handler_with_results.data[
        "to_target_timestamps"
    ][0][0]:
        assert (
            timestamps[-1]
            < 0.5 * experiment_no_results.trial_list[0]["target_duration"]
        )


def test_task_no_central_target(
    experiment_no_results: Experiment, window: Window
) -> None:
    target_pixels = []
    experiment_no_results.has_unsaved_changes = False
    assert experiment_no_results.trial_handler_with_results is None
    for trial in experiment_no_results.trial_list:
        trial["add_central_target"] = False
        trial["automove_cursor_to_center"] = False
        trial["weight"] = 1
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
    task = MotorTask(experiment_no_results, window)
    success = task.run()
    do_task_thread.join()
    # task ran successfully, updated experiment with results
    assert success is True
    assert experiment_no_results.has_unsaved_changes is True
    assert experiment_no_results.trial_handler_with_results is not None
    # check that we hit all the targets without timing out
    for timestamps in experiment_no_results.trial_handler_with_results.data[
        "to_target_timestamps"
    ][0][0]:
        assert (
            timestamps[-1]
            < 0.5 * experiment_no_results.trial_list[0]["target_duration"]
        )


def test_task_no_automove_to_center(
    experiment_no_results: Experiment, window: Window
) -> None:
    experiment_no_results.has_unsaved_changes = False
    assert experiment_no_results.trial_handler_with_results is None
    target_pixels = []
    for trial in experiment_no_results.trial_list:
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
    task = vstt.task.MotorTask(experiment_no_results, window)
    success = task.run()
    do_task_thread.join()
    # task ran successfully, updated experiment with results
    assert success is True
    assert experiment_no_results.has_unsaved_changes is True
    assert experiment_no_results.trial_handler_with_results is not None
    # check that we hit all the targets
    for to_target_timestamps, to_center_timestamps in zip(
        experiment_no_results.trial_handler_with_results.data["to_target_timestamps"][
            0
        ][0],
        experiment_no_results.trial_handler_with_results.data["to_center_timestamps"][
            0
        ][0],
    ):
        assert (
            to_target_timestamps[-1]
            < 0.5 * experiment_no_results.trial_list[0]["target_duration"]
        )
        assert (
            to_center_timestamps[-1]
            < 0.5 * experiment_no_results.trial_list[0]["target_duration"]
        )


def test_task_fixed_intervals_no_user_input(window: Window) -> None:
    experiment = Experiment()
    experiment.metadata["display_duration"] = 0.0
    target_duration = 1.0
    trial = vstt.trial.default_trial()
    trial["num_targets"] = 3
    trial["target_order"] = "random"
    trial["show_target_labels"] = True
    trial["fixed_target_intervals"] = True
    trial["target_duration"] = target_duration
    trial["automove_cursor_to_center"] = False
    trial["freeze_cursor_between_targets"] = False
    trial["post_block_delay"] = 0.0
    trial["play_sound"] = False
    experiment.trial_list = [trial]
    assert experiment.trial_handler_with_results is None
    task = vstt.task.MotorTask(experiment, window)
    # run task without moving mouse, which will stay in center for entire experiment
    assert task.run() is True
    # task ran successfully, updated experiment with results
    assert experiment.has_unsaved_changes is True
    assert experiment.trial_handler_with_results is not None
    # check that we failed to hit all targets
    expected_success = np.full((trial["num_targets"],), False)
    for success_name in ["to_target_success", "to_center_success"]:
        assert np.all(
            experiment.trial_handler_with_results.data[success_name][0][0]
            == expected_success
        )
    # first to_target timestamps should start at approx -target_duration,
    # at 0 the first target is displayed for target_duration secs, so it should end at approx target_duration
    # subsequent ones should start at approx 0.0 since previous target is not reached, and end at approx target_duration
    all_to_target_timestamps = experiment.trial_handler_with_results.data[
        "to_target_timestamps"
    ][0][0]
    delta = 0.05 * target_duration
    assert abs(all_to_target_timestamps[0][0] + target_duration) < delta
    assert abs(all_to_target_timestamps[0][-1] - target_duration) < delta
    for to_target_timestamps in all_to_target_timestamps[1:]:
        assert abs(to_target_timestamps[0]) < delta
        assert abs(to_target_timestamps[-1] - target_duration) < delta
