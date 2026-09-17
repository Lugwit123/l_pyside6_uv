# -*- coding: utf-8 -*-
# === wuwo doc_pkg BEGIN v7 (auto-generated, do not edit) ===
# 包：l_pyside6_uv 999.0  PySide6 development scaffold managed by uv (click-to-run uv commands)
# 依赖：python-3.9+, pyside6, qtpy
# 提供：PYTHONPATH {root}/src；env PYSIDE6_UV_ROOT；PYTHONIOENCODING=utf-8
# 入口：l_pyside6_uv
# 用法：wuwo l_pyside6_uv 进入该包环境；wuwor l_pyside6_uv -- l_pyside6_uv 直接调用别名
# 查文档：全量搜索（笔记+全部知识库）：curl "http://127.0.0.1:8765/api/search?q=<关键词>&limit=10" → hits[].kb_name / rel
#     只搜本仓文档：curl "http://127.0.0.1:8765/api/kb/rez_pkg/search?q=<关键词>&limit=10"
#     读正文：curl "http://127.0.0.1:8765/api/kb/<kb_name>/workspace/file?path=<rel>"（参数名 path，不是 rel）
#     本机直连 8765 免 token（仅 GET，勿经 nginx）；q 要 URL 编码；score < 1.0 多为向量噪声
#     接口全表与踩坑见 D:/TD_Depot/Software/Lugwit_syncPlug/lugwit_insapp/trayapp/rez-package-source/Rez-Docs/Rez_pkg/l_notepad_搜索接口使用文档.md
# 跑代码：远程连上宿主程序，用宿主解释器跑代码（依赖与 Qt 事件循环齐备），别自己另起解释器
#     探活：curl http://127.0.0.1:8764/status（多实例逐个试 8764 / 8769；editor_available=true 才可用）
#     执行：curl -H "Content-Type: application/json" -d "{\"code\": \"print(1)\"}" http://127.0.0.1:8764/execute
#     长代码先落盘再 exec(open(r'<abs.py>', encoding='utf-8').read())，避免 JSON 转义地狱
#     其它工具：/execute_async 异步、/upload /upload_folder /download 传文件、/tools 列 agent 工具
#     UI 自动化（Qt 版 Playwright）：/ui/tree 控件树、/ui/locate 定位、/ui/action click|set_text|press_key、/ui/wait auto-wait、/ui/screenshot 截图
#     全表见 D:/TD_Depot/Software/Lugwit_syncPlug/lugwit_insapp/trayapp/rez-package-source/Rez-Docs/Rez_pkg/l_script_editor.md
# 建包：新建/改包前先读 D:/TD_Depot/Software/Lugwit_syncPlug/lugwit_insapp/trayapp/rez-package-source/Rez-Docs/Rez包创建和启动指导文档.md
#    覆盖：目录布局 <包名>/<版本>/package.py、requires 写法、alias/env、变体哈希、修饰符与启动方式
# 规范：999.0 源码即环境（改源码即生效，无需 build）；依赖写进 requires 由 wuwo 自动补齐
#    修饰符 .dev_mod / .solo / .soloignore / .script_server 与建包规范见 Rez-Docs/Rez包创建和启动指导文档.md
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
