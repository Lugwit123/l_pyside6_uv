# -*- coding: utf-8 -*-
# === wuwo doc_pkg BEGIN v3 (auto-generated, do not edit) ===
# 包：l_pyside6_uv 999.0  PySide6 development scaffold managed by uv (click-to-run uv commands)
# 依赖：python-3.9+, pyside6, qtpy
# 提供：PYTHONPATH {root}/src；env PYSIDE6_UV_ROOT；PYTHONIOENCODING=utf-8
# 入口：l_pyside6_uv
# 用法：wuwo l_pyside6_uv 进入该包环境；wuwor l_pyside6_uv -- l_pyside6_uv 直接调用别名
# 规范：999.0 源码即环境（改源码即生效，无需 build）；依赖写进 requires 由 wuwo 自动补齐
#    修饰符 .dev_mod / .solo / .script_server 与建包规范见 Rez-Docs/Rez包创建和启动指导文档.md
# === wuwo doc_pkg END ===

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
