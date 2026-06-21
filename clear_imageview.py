#!/usr/bin/env python3

from pathlib import Path

config_file = Path.home() / ".config" / "ros.org" / "rqt_gui.ini"

if not config_file.exists():
    print("RQt config not found")
    exit(0)

lines = config_file.read_text().splitlines()

with config_file.open("w") as f:
    for line in lines:
        if (
            r"plugin__rqt_image_view__ImageView__1\plugin\topic="
            in line
        ):
            f.write(
                r"Default\pluginmanager\plugin__rqt_image_view__ImageView__1\plugin\topic="
                "\n"
            )
        else:
            f.write(line + "\n")