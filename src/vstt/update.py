from __future__ import annotations

import logging
import subprocess
import sys

import requests
from packaging import version

import vstt


def _get_latest_pypi_version() -> version.Version:
    logging.info("Requesting latest version from pypi...")
    r = requests.get("https://pypi.org/pypi/vstt/json", timeout=5)
    version_str = r.json().get("info", {}).get("version", "")
    ver = version.parse(version_str)
    logging.info(f"  -> {ver}")
    return ver


def check_for_new_version() -> tuple[bool, str]:
    try:
        current_version = version.Version(vstt.__version__)
        logging.info(f"Current version: {current_version}")
        latest_version = _get_latest_pypi_version()
        logging.info(f"Latest version: {latest_version}")
        if latest_version > current_version:
            return (
                True,
                f"Latest version of VSTT: {latest_version}.\nYou currently have version {current_version}.\nWould you like to upgrade now?",
            )
        else:
            return (
                False,
                "You have the latest version of VSTT.",
            )
    except Exception as e:
        logging.exception(e)
        return (
            False,
            "An error occurred while checking for updates, please try again later.",
        )


def do_pip_upgrade() -> tuple[bool, str]:
    logging.info(f"Doing pip upgrade using {sys.executable}...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", "vstt"]
        )
        logging.info("done.")
        return (
            True,
            "VSTT has been updated.\nPlease close the program and open it again to see the latest version.",
        )
    except Exception as e:
        logging.exception(e)
        return False, f"An error occurred when trying to update VSTT: {e}"
