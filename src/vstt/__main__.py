from __future__ import annotations

import logging

import click
from psychopy.gui.qtgui import ensureQtApp
from qtpy import QtWidgets

from vstt.gui import Gui


@click.command()
@click.argument("filename", required=False)
def main(filename: str | None) -> None:
    logging.basicConfig(
        format="%(levelname)s %(module)s.%(funcName)s.%(lineno)d :: %(message)s"
    )
    ensureQtApp()
    app = QtWidgets.QApplication.instance()
    assert app is not None
    gui = Gui(filename=filename)
    gui.showMaximized()
    app.exec()


if __name__ == "__main__":
    main()
