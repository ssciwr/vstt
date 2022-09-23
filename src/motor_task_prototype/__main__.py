import logging

import click
from motor_task_prototype.gui import MotorTaskGui
from psychopy.gui.qtgui import ensureQtApp
from PyQt5 import QtWidgets


@click.command()
@click.argument("filename", required=False)
def main(filename: str) -> None:
    logging.basicConfig(
        format="%(levelname)s %(module)s.%(funcName)s.%(lineno)d :: %(message)s"
    )
    ensureQtApp()
    app = QtWidgets.QApplication.instance()
    assert app is not None
    gui = MotorTaskGui(filename)
    gui.show()
    app.exec()


if __name__ == "__main__":
    main()
