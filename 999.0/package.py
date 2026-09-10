# -*- coding: utf-8 -*-
# Rez root = this directory (999.0). uv-managed PySide6 development scaffold.
# NOTE: this is a dev scaffold, NOT the `pyside6` rez-package-3rd meta package.
# It uses uv for dependency/venv management instead of rez `requires`.

name = "l_pyside6_uv"
version = "999.0"
description = "PySide6 development scaffold managed by uv (click-to-run uv commands)"
authors = ["Lugwit Team"]

requires = ["python-3.9+", "pyside6", "qtpy"]

build_command = False
cachable = True
relocatable = True


def commands():
    env.PYTHONPATH.append("{root}/src")
    env.PYSIDE6_UV_ROOT = "{root}"
    env.PYTHONIOENCODING = "utf-8"
    alias("l_pyside6_uv", 'cmd /c "set PYTHONHOME=& set PYTHONPATH=& set PYTHONEXECUTABLE=& cd /d {root} && uv run python -m l_pyside6_uv.main"')
