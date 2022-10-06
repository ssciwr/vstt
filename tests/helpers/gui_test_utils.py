from __future__ import annotations

import queue
import sys
import threading
from time import sleep
from typing import Callable
from typing import Tuple

import ascii_magic
from psychopy.visual.window import Window

if sys.platform.startswith("win"):
    # use alternative library to generate keyboard events on windows
    import keyboard
import numpy as np
import pyautogui


# print screenshot as ascii art to terminal for debugging
def ascii_screenshot() -> None:
    print(f"\n{ascii_magic.from_image(pyautogui.screenshot())}\n", flush=True)


# simulate user pressing Enter key
def press_enter() -> None:
    if sys.platform.startswith("win"):
        # `keyboard` works on windows but needs sudo on linux
        keyboard.send("enter")
    else:
        # `pyautogui` in principle works everywhere, but
        # key events don't seem to do actually do anything on windows
        pyautogui.press("enter")


# return true if pixel or any neighbours is of the desired color
def pixel_color(pixel: Tuple[float, float], color: Tuple[int, int, int]) -> bool:
    img = pyautogui.screenshot().load()
    for dx in [0, 1, -1]:
        for dy in [0, 1, -1]:
            p = (pixel[0] + dx, pixel[1] + dy)
            if np.allclose(img[p], color):
                return True
    return False


# convert a position in units of screen height to a pair of pixels
def pos_to_pixels(pos: Tuple[float, float]) -> Tuple[float, float]:
    # pos is in units of screen height, with 0,0 in centre of screen
    width, height = pyautogui.size()
    # return equivalent position in pixels with 0,0 in top left of screen
    pixels = width / 2.0 + pos[0] * height, height / 2.0 - pos[1] * height
    return pixels


# RMS difference between two arrays
def rms_diff(a: np.ndarray, b: np.ndarray) -> float:
    return np.sqrt(np.mean(np.square(a - b)))


# wait for screen to change, return screenshot
def get_screenshot_when_ready(
    screenshot_before: np.ndarray,
    screenshot_queue: queue.Queue,
    min_rms_diff: float = 0.1,
    delay_between_screenshots: float = 0.5,
) -> None:
    s0 = np.asarray(screenshot_before)
    sleep(delay_between_screenshots)
    img = pyautogui.screenshot()
    s1 = np.asarray(img)
    # wait until
    #   - screen differs significantly from original screenshot
    #   - is not all black (xvfb initial screen)
    #   - is not all grey (psychopy initial screen)
    black = 0.0
    grey = 128.0
    attempts = 0
    while rms_diff(s1, s0) < min_rms_diff or np.mean(s1) in [black, grey]:
        sleep(delay_between_screenshots)
        img = pyautogui.screenshot()
        s1 = np.asarray(img)
        attempts += 1
        if attempts > 10:
            print("Stuck waiting for screen to be ready", flush=True)
            print(f"Mean pixel: {np.mean(s1)}", flush=True)
            ascii_screenshot()
    print(f"\n{ascii_magic.from_image(img)}\n", flush=True)
    screenshot_queue.put(s1)
    # press enter to close screen
    press_enter()
    sleep(delay_between_screenshots)
    # wait for enter key press to take effect
    attempts = 0
    while screenshot_pixel_color_fraction((128, 128, 128)) != 1:
        sleep(delay_between_screenshots)
        attempts += 1
        if attempts > 10:
            # sometimes (on windows CI) the enter key event seems to get lost
            # and the screen never closes - in this case we try pressing it again
            # but with a long pause after each enter press
            # to try to avoid it arriving during the next test
            print("Stuck waiting for screen to close: pressing Enter again", flush=True)
            print(
                f"Mean pixel: {np.mean(np.asarray(pyautogui.screenshot()))}", flush=True
            )
            ascii_screenshot()
            press_enter()
            delay_after_repeat_enter_press = 15
            sleep(delay_after_repeat_enter_press)
    return


# call target with args, get screenshot when ready, press Enter to close screen
def call_target_and_get_screenshot(
    target: Callable, args: Tuple, win: Window
) -> np.ndarray:
    screenshot_queue: queue.Queue = queue.Queue()
    screenshot_before = pyautogui.screenshot()
    screenshot_thread = threading.Thread(
        target=get_screenshot_when_ready,
        name="display_results",
        args=(screenshot_before, screenshot_queue),
    )
    screenshot_thread.start()
    target(*args)
    # flip window when finished to make screen all-grey
    win.flip()
    screenshot_thread.join()
    return screenshot_queue.get()


# return fraction of pixels in image of the supplied color
def pixel_color_fraction(img: np.ndarray, color: Tuple[int, int, int]) -> float:
    return np.count_nonzero((img == np.array(color)).all(axis=2)) / (img.size / 3)


# return fraction of pixels in current screen of the supplied color
def screenshot_pixel_color_fraction(color: Tuple[int, int, int]) -> float:
    return pixel_color_fraction(np.asarray(pyautogui.screenshot()), color)
