from psychopy.gui import DlgFromDict
from psychopy.visual.window import Window
from psychopy.visual.circle import Circle
from psychopy.visual.line import Line
from psychopy.visual.shape import ShapeStim
from psychopy.sound import Sound
from psychopy.clock import Clock
from psychopy import core
from psychopy.event import Mouse, xydist
from psychopy.hardware.keyboard import Keyboard
import psychtoolbox as ptb
from motor_task_prototype.geometry import points_on_circle, rotate_point
from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum
import numpy as np


def make_cursor(window: Window) -> ShapeStim:
    return ShapeStim(
        window,
        lineColor="black",
        pos=(0, 0),
        lineWidth=5,
        vertices=[
            (-0.01, 0.00),
            (0.01, 0.00),
            (0.00, 0.00),
            (0.00, -0.01),
            (0.00, 0.01),
        ],
        closeShape=False,
    )


def make_targets(
    window: Window,
    n_circles: int,
    radius: float,
    point_radius: float,
    center_point_radius: float,
) -> List[Circle]:
    circles = []
    for pos in points_on_circle(n_circles, radius):
        circles.append(
            Circle(window, radius=point_radius, pos=pos, lineColor="black", lineWidth=3)
        )
    circles.append(
        Circle(
            window,
            radius=center_point_radius,
            pos=(0, 0),
            lineColor="black",
            lineWidth=3,
        )
    )
    return circles


def select_target(targets, index=None) -> None:
    for target in targets:
        target.setFillColor("none")
    if index is not None:
        targets[index].setFillColor("red")


def draw_and_flip(win, drawables, kb):
    for drawable in drawables:
        drawable.draw()
    if kb.getKeys(["escape"]):
        core.quit()
    win.flip()


class TargetOrder(Enum):
    CLOCKWISE = "Clockwise"
    ANTICLOCKWISE = "Anti-clockwise"
    RANDOM = "Random"


@dataclass
class MotorTaskSettings:
    n_points: int = 8
    order_of_targets: TargetOrder = TargetOrder.CLOCKWISE
    time_per_point: float = 5
    time_between_points: float = 2
    outer_radius: float = 0.45
    point_radius: float = 0.04
    center_point_radius: float = 0.02
    play_sound: bool = True
    show_cursor: bool = True
    show_cursor_line: bool = True
    rotate_cursor_radians: float = 0


@dataclass
class MotorTaskTargetResult:
    target_index: int
    target_position: Tuple[float, float]
    mouse_times: List[float]
    mouse_positions: List[Tuple[float, float]]


def get_settings_from_user(
    settings: MotorTaskSettings = MotorTaskSettings(),
) -> MotorTaskSettings:
    order_of_targets = [settings.order_of_targets.value]
    for target_order in TargetOrder:
        if target_order != settings.order_of_targets:
            order_of_targets.append(target_order.value)
    dialog_dict = {
        "Number of targets": settings.n_points,
        "Order of targets": order_of_targets,
        "Target Duration (secs)": 5,
        "Interval between targets (secs)": 2,
        "Distance of targets (screen height)": 0.45,
        "Size of targets (screen height)": 0.04,
        "Size of center point (screen height)": 0.02,
        "Audible tone on target display": ["Yes", "No"],
        "Display cursor": ["Yes", "No"],
        "Display cursor path": ["Yes", "No"],
        "Rotate cursor (degrees)": 0,
    }
    dialog = DlgFromDict(dialog_dict, title="Motor task settings", sortKeys=False)
    if dialog.OK:
        settings.n_points = dialog_dict["Number of targets"]
        settings.order_of_targets = TargetOrder(dialog_dict["Order of targets"])
        settings.time_per_point = dialog_dict["Target Duration (secs)"]
        settings.time_between_points = dialog_dict["Interval between targets (secs)"]
        settings.outer_radius = dialog_dict["Distance of targets (screen height)"]
        settings.point_radius = dialog_dict["Size of targets (screen height)"]
        settings.center_point_radius = dialog_dict[
            "Size of center point (screen height)"
        ]
        settings.play_sound = dialog_dict["Audible tone on target display"] == "Yes"
        settings.show_cursor = dialog_dict["Display cursor"] == "Yes"
        settings.show_cursor_line = dialog_dict["Display cursor path"] == "Yes"
        settings.rotate_cursor_radians = dialog_dict["Rotate cursor (degrees)"] * (
            2.0 * np.pi / 360.0
        )
    return settings


class MotorTask:
    settings: MotorTaskSettings
    target_indices: np.array

    def __init__(self, settings: MotorTaskSettings = MotorTaskSettings()):
        self.settings = settings
        self.target_indices = np.array(range(self.settings.n_points))
        if self.settings.order_of_targets == TargetOrder.ANTICLOCKWISE:
            self.target_indices = np.flip(self.target_indices)
        elif self.settings.order_of_targets == TargetOrder.RANDOM:
            rng = np.random.default_rng()
            rng.shuffle(self.target_indices)

    def run(self, win) -> List[MotorTaskTargetResult]:
        results = []
        mouse = Mouse(visible=False)
        clock = Clock()
        kb = Keyboard()
        targets = make_targets(
            win,
            self.settings.n_points,
            self.settings.outer_radius,
            self.settings.point_radius,
            self.settings.center_point_radius,
        )
        drawables = targets
        cursor = make_cursor(win)
        if self.settings.show_cursor:
            drawables.append(cursor)
        for target_index in self.target_indices:
            result = MotorTaskTargetResult(
                target_index, targets[target_index].pos, [], []
            )
            select_target(targets, None)
            drawables = [x for x in drawables if type(x) != Line]
            cursor.setPos((0.0, 0.0))
            clock.reset()
            clock.add(self.settings.time_between_points)
            while clock.getTime() < 0:
                draw_and_flip(win, drawables, kb)
            clock.reset()
            clock.add(self.settings.time_per_point)
            select_target(targets, target_index)
            if self.settings.play_sound:
                Sound("A", secs=0.3, blockSize=512).play()
            t0 = clock.getTime()
            mouse_pos = (0.0, 0.0)
            dist = xydist(mouse_pos, targets[target_index].pos)
            result.mouse_times.append(0)
            result.mouse_positions.append(mouse_pos)
            mouse.setPos(mouse_pos)
            win.flip()
            mouse.setPos(mouse_pos)
            while dist > self.settings.point_radius and clock.getTime() < 0:
                prev_mouse_pos = mouse_pos
                mouse_pos = mouse.getPos()
                if self.settings.rotate_cursor_radians != 0:
                    mouse_pos = rotate_point(
                        mouse_pos, self.settings.rotate_cursor_radians
                    )
                if self.settings.show_cursor:
                    cursor.setPos(mouse_pos)
                if self.settings.show_cursor_line:
                    drawables.append(Line(win, prev_mouse_pos, mouse_pos))
                result.mouse_times.append(clock.getTime() - t0)
                result.mouse_positions.append(mouse_pos)
                dist = xydist(mouse_pos, targets[target_index].pos)
                draw_and_flip(win, drawables, kb)
            results.append(result)
        win.flip()
        return results
