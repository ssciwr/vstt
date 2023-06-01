from __future__ import annotations

import logging
from typing import Optional

import click
from psychopy.gui.qtgui import ensureQtApp
from PyQt5 import QtWidgets
from vstt.gui import Gui


@click.command()
@click.argument("filename", required=False)
def main(filename: Optional[str]) -> None:
    logging.basicConfig(
        format="%(levelname)s %(module)s.%(funcName)s.%(lineno)d :: %(message)s"
    )
    ensureQtApp()
    app = QtWidgets.QApplication.instance()
    assert app is not None
    gui = Gui(filename=filename)
    gui.show()
    app.exec()


if __name__ == "__main__":
    main()
