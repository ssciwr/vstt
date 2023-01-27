from __future__ import annotations

import logging
from typing import Optional

import click
from motor_task_prototype import config as mtpconfig
from motor_task_prototype.gui import MotorTaskGui
from psychopy.gui.qtgui import ensureQtApp
from PyQt5 import QtWidgets


@click.command()
@click.option(
    "--win-type",
    type=click.Choice(["pyglet", "glfw"], case_sensitive=False),
    required=False,
    default="pyglet",
)
@click.argument("filename", required=False)
def main(filename: Optional[str], win_type: str) -> None:
    logging.basicConfig(
        format="%(levelname)s %(module)s.%(funcName)s.%(lineno)d :: %(message)s"
    )
    ensureQtApp()
    app = QtWidgets.QApplication.instance()
    assert app is not None
    mtpconfig.win_type = win_type
    gui = MotorTaskGui(filename=filename)
    gui.show()
    app.exec()


if __name__ == "__main__":
    main()
