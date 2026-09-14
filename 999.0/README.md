# l_pyside6_uv

# === wuwo doc_pkg BEGIN v3 (auto-generated, do not edit) ===
# 包：l_pyside6_uv 999.0  PySide6 development scaffold managed by uv (click-to-run uv commands)
# 依赖：python-3.9+, pyside6, qtpy
# 提供：PYTHONPATH {root}/src；env PYSIDE6_UV_ROOT；PYTHONIOENCODING=utf-8
# 入口：l_pyside6_uv
# 用法：wuwo l_pyside6_uv 进入该包环境；wuwor l_pyside6_uv -- l_pyside6_uv 直接调用别名
# 规范：999.0 源码即环境（改源码即生效，无需 build）；依赖写进 requires 由 wuwo 自动补齐
#    修饰符 .dev_mod / .solo / .script_server 与建包规范见 Rez-Docs/Rez包创建和启动指导文档.md
# === wuwo doc_pkg END ===

PySide6 开发脚手架包，由 **uv**（Python 包管理器）管理虚拟环境与依赖。
放在 `rez-package-source` 下，同时保留了 Rez 包结构（`package.py`），
但日常开发/运行走 uv，而不是 rez `requires`。

> 命名说明：为避免与 `rez-package-3rd` 中已有的 `pyside6` 元包冲突，
> 本包命名为 `l_pyside6_uv`。

## 目录结构

```
l_pyside6_uv/999.0/
  package.py            # Rez 声明（最小化，保留 rez 兼容）
  pyproject.toml        # uv 项目配置（src 布局，依赖 PySide6）
  README.md
  .gitignore
  src/l_pyside6_uv/     # Python 源码包
    __init__.py
    main.py             # 入口：启动一个简单 PySide6 窗口
  ui/                   # 放 *.ui（Qt Designer）
  resources/            # 放 *.qrc / 图标等资源
  scripts/              # 常用 uv 命令的 .bat（可双击运行）
```

## 命令启动器界面

应用本身是一个 **uv 命令启动器**：窗口左侧列出预设的常用 uv 命令，
双击（或选中后点「运行所选」）即在窗口内执行并实时显示输出。
预设命令包括 `uv sync`、`uv add PySide6`、`uv add --dev`、
`uv lock --upgrade`、`uv build`、查看 PySide6 版本、打开 Qt Designer 等。
命令均在项目根目录下运行。新增命令只需编辑 `src/l_pyside6_uv/main.py` 里的 `COMMANDS` 列表。

## 快速开始（双击运行）

进入 `scripts\` 目录，按编号双击即可（脚本自动 `cd` 到项目根目录并 `pause`）：

| 脚本 | 作用 |
|------|------|
| `00_uv_sync.bat` | `uv sync` 安装/同步依赖（首次运行用这个） |
| `01_uv_run_app.bat` | 启动 PySide6 应用 |
| `02_uv_add_pyside6.bat` | `uv add PySide6` 添加/升级 PySide6 依赖 |
| `03_uv_add_dev.bat` | 添加开发依赖（示例：pyinstaller） |
| `04_uv_run_designer.bat` | 打开 Qt Designer（可视化编辑 UI） |
| `05_uv_compile_ui.bat` | 把 `ui\*.ui` 编译为 `l_pyside6_uv\ui_*.py` |
| `06_uv_compile_resources.bat` | 把 `resources\*.qrc` 编译为 `l_pyside6_uv\resources_rc.py` |
| `07_uv_update_lock.bat` | `uv lock --upgrade` 升级所有依赖并更新锁文件 |
| `08_uv_build.bat` | `uv build` 构建 wheel / sdist |
| `09_uv_doctor.bat` | 自检：确认 uv、PySide6 已就绪 |

## 命令行等价操作

```bat
cd /d <本包目录>                     :: 即 ...\rez-package-source\l_pyside6_uv\999.0
uv sync                             :: 安装依赖（生成 .venv）
uv run python -m l_pyside6_uv.main  :: 运行应用
uv add PySide6                      :: 新增/升级依赖
uv add --dev pyinstaller            :: 新增开发依赖
uv run pyside6-designer             :: Qt Designer
uv run pyside6-uic ui\demo.ui -o src\l_pyside6_uv\ui_demo.py
uv run pyside6-rcc resources\demo.qrc -o src\l_pyside6_uv\resources_demo_rc.py
uv lock --upgrade                   :: 升级全部依赖
uv build                            :: 构建发布包
```

## Rez 侧（可选）

包内 `package.py` 仍可被 wuwo/rez 识别：

```bat
wuwor l_pyside6_uv -- l_pyside6_uv
```

但依赖解析走 uv（`uv sync`）而非 rez `requires`，两者互不干扰。
