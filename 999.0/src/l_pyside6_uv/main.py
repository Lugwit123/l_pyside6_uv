"""PySide6 uv command launcher.

A GUI that lists preset `uv` commands and runs the selected one, streaming
its output into the window. Designed for the l_pyside6_uv scaffold so you can
drive common uv tasks (sync / add / lock / build / designer ...) by clicking.

Features: search filter, favorites (pinned to top, persisted), custom commands
(add/edit/delete, persisted), running state + stop, colored exit code/elapsed,
and parameter input popup for placeholder args like <pkg>.

Run with uv:
    uv run python -m l_pyside6_uv.main
    uv run l-pyside6-uv
"""

import json
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

from PySide6.QtCore import QProcess, QProcessEnvironment, Qt
from PySide6.QtGui import QBrush, QColor, QFont
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QStyledItemDelegate,
    QVBoxLayout,
    QWidget,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VENV_DIR = PROJECT_ROOT / ".venv"
FAV_FILE = PROJECT_ROOT / ".uv_launcher_favorites.json"
CUSTOM_FILE = PROJECT_ROOT / ".uv_launcher_custom.json"
SIZE_FILE = PROJECT_ROOT / ".uv_launcher_settings.json"

DARK_QSS = """
QWidget { background-color: #1e1e1e; color: #d4d4d4; }
QMainWindow { background-color: #1e1e1e; }
QListWidget { background-color: #252526; border: 1px solid #3c3c3c; }
QListWidget::item { padding: 4px 6px; }
QListWidget::item:selected { background-color: #094771; color: #ffffff; }
QListWidget::item:hover { background-color: #2a2d2e; }
QPushButton { background-color: #3c3c3c; border: 1px solid #3c3c3c; border-radius: 4px; padding: 6px 10px; }
QPushButton:hover { background-color: #4a4a4a; }
QPushButton:pressed { background-color: #555555; }
QLineEdit { background-color: #3c3c3c; border: 1px solid #3c3c3c; border-radius: 4px; padding: 4px; }
QLineEdit:focus { border: 1px solid #094771; }
QPlainTextEdit { background-color: #1e1e1e; border: 1px solid #3c3c3c; color: #cccccc; }
QDialog { background-color: #252526; }
QLabel { background-color: transparent; }
QToolTip { background-color: #2d2d2d; color: #d4d4d4; border: 1px solid #3c3c3c; }
"""

BUILTIN = [
    # --- 项目依赖 ---
    ("uv init  创建新项目", ["init"]),
    ("uv add PySide6  添加/升级依赖", ["add", "PySide6"]),
    ("uv add --dev pyinstaller  添加开发依赖", ["add", "--dev", "pyinstaller"]),
    ("uv add 常用库(numpy pandas 等)  一键装常用库", ["add", "numpy", "pandas", "matplotlib", "requests", "scipy", "scikit-learn", "pillow", "openpyxl", "tqdm"]),
    ("uv remove <pkg>  移除依赖", ["remove", "pytest"]),
    ("uv sync  安装/同步依赖", ["sync"]),
    ("uv lock  更新锁文件", ["lock"]),
    ("uv lock --upgrade  升级全部依赖", ["lock", "--upgrade"]),
    ("uv export  导出 requirements.txt", ["export", "--format", "requirements-txt", "-o", "requirements.txt"]),
    ("uv tree  依赖树", ["tree"]),
    ("uv version  项目版本", ["version"]),
    ("uv version --bump patch  版本号+1", ["version", "--bump", "patch"]),
    ("uv format  格式化代码", ["format"]),
    # --- 运行 ---
    ("uv run python -m l_pyside6_uv.main  再启动一个本应用", ["run", "python", "-m", "l_pyside6_uv.main"]),
    ("uv run pyside6-designer  打开 Qt Designer", ["run", "pyside6-designer"]),
    ("uv run python -c 查看 PySide6 版本", ["run", "python", "-c", "import PySide6; print('PySide6', PySide6.__version__)"]),
    ("uv run python -c 查看虚拟环境路径", ["run", "python", "-c", "import sys, os; print('exe :', sys.executable); print('venv:', os.environ.get('VIRTUAL_ENV', '(未设置)'))"]),
    ("uv run <script>  运行脚本", ["run", "python", "-c", "print('hello from uv run')"]),
    # --- 环境 / 解释器 ---
    ("uv venv  创建虚拟环境", ["venv"]),
    ("uv python list  已安装 Python", ["python", "list"]),
    ("uv python install 3.13  安装 Python", ["python", "install", "3.13"]),
    ("uv python find  定位 Python", ["python", "find"]),
    # --- 环境切换示例（独立环境 .venv312）---
    ("环境切换 1: 新建独立环境 .venv312 (python 3.12)", ["venv", ".venv312", "--python", "3.12"]),
    ("环境切换 2: 在 .venv312 里运行", ["run", "--no-sync", "python", "-c", "import sys; print('当前环境:', sys.executable)"]),
    ("环境切换 3: 往 .venv312 里装包 (pip install requests)", ["pip", "install", "requests"]),
    ("环境切换 4: 回到默认 .venv 运行", ["run", "python", "-c", "import sys; print('当前环境:', sys.executable)"]),
    # --- pip 接口 ---
    ("uv pip list  列出已装包", ["pip", "list"]),
    ("uv pip freeze  冻结依赖", ["pip", "freeze"]),
    ("uv pip install <pkg>  安装包", ["pip", "install", "requests"]),
    ("uv pip compile  编译锁定", ["pip", "compile", "pyproject.toml"]),
    ("uv pip sync  同步环境", ["pip", "sync"]),
    # --- 工具 (tool) ---
    ("uv tool list  已安装工具", ["tool", "list"]),
    ("uv tool install ruff  安装工具", ["tool", "install", "ruff"]),
    ("uv tool run ruff  临时运行工具", ["tool", "run", "ruff"]),
    # --- 构建 / 发布 ---
    ("uv build  构建发布包", ["build"]),
    ("uv publish  发布到索引", ["publish"]),
    # --- 缓存 / 自身 / 认证 / 其它 ---
    ("uv cache dir  缓存目录", ["cache", "dir"]),
    ("uv cache clean  清空缓存", ["cache", "clean"]),
    ("uv cache prune  清理过期缓存", ["cache", "prune"]),
    ("uv self update  更新 uv 自身", ["self", "update"]),
    ("uv auth login  登录", ["auth", "login"]),
    ("uv auth logout  登出", ["auth", "logout"]),
    ("uv --version  uv 版本", ["--version"]),
    ("uv help  帮助", ["help"]),
]


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


# 部分内置命令的补充提示：desc 说明 / prereq 前提 / params 参数含义
META = {
    "uv init  创建新项目": {"prereq": "在空目录/新项目运行；若已有 pyproject.toml 会报错"},
    "uv add PySide6  添加/升级依赖": {"desc": "把 PySide6 写进 pyproject.toml 并安装"},
    "uv add --dev pyinstaller  添加开发依赖": {"prereq": "需已有项目(pyproject.toml)"},
    "uv add 常用库(numpy pandas 等)  一键装常用库": {
        "desc": "把 numpy/pandas/matplotlib/requests/scipy 等常用库写入 pyproject.toml 并安装，使默认解释器开箱即用",
        "prereq": "需网络；首次会下载较多包",
    },
    "uv remove <pkg>  移除依赖": {"params": {"<pkg>": "要移除的包名"}, "prereq": "该包需已在依赖中"},
    "uv sync  安装/同步依赖": {"prereq": "首次运行会创建 .venv 并联网下载"},
    "uv lock --upgrade  升级全部依赖": {"prereq": "需网络；会改写 uv.lock"},
    "uv export  导出 requirements.txt": {"prereq": "需先 uv lock 生成锁文件"},
    "uv run python -m l_pyside6_uv.main  再启动一个本应用": {"prereq": "需先 uv sync"},
    "uv run pyside6-designer  打开 Qt Designer": {"prereq": "需先 uv sync（安装 PySide6）"},
    "uv run python -c 查看 PySide6 版本": {"prereq": "需先 uv sync"},
    "uv run <script>  运行脚本": {"params": {"<script>": "要运行的脚本路径"}},
    "uv python install 3.13  安装 Python": {"prereq": "需网络下载解释器"},
    "uv pip install <pkg>  安装包": {"params": {"<pkg>": "要安装的包名"}},
    "uv pip compile  编译锁定": {"prereq": "需已有 pyproject.toml"},
    "uv pip sync  同步环境": {"prereq": "需先用 uv pip compile 生成锁文件"},
    "uv build  构建发布包": {"prereq": "需先 uv sync；输出在 dist/"},
    "uv publish  发布到索引": {"prereq": "需已配置索引凭证(uv auth login)"},
    "uv cache clean  清空缓存": {"prereq": "不会删除 .venv，仅清全局缓存"},
    "uv self update  更新 uv 自身": {"prereq": "需网络"},
    "uv auth login  登录": {"prereq": "需配置远程索引地址"},
    "环境切换 1: 新建独立环境 .venv312 (python 3.12)": {
        "desc": "创建独立虚拟环境 .venv312（不覆盖默认 .venv）",
        "prereq": "首次会联网下载 CPython 3.12",
    },
    "环境切换 2: 在 .venv312 里运行": {
        "desc": "通过 UV_PROJECT_ENVIRONMENT 指向 .venv312 运行",
        "prereq": "需先执行「环境切换 1」创建 .venv312",
    },
    "环境切换 3: 往 .venv312 里装包 (pip install requests)": {
        "desc": "把 requests 装进 .venv312 而非默认 .venv",
        "prereq": "需先执行「环境切换 1」创建 .venv312",
    },
    "环境切换 4: 回到默认 .venv 运行": {
        "desc": "不设 UV_PROJECT_ENVIRONMENT，使用默认 .venv",
    },
}


# 环境切换: 为指定命令注入额外环境变量（如指向独立 venv）
ENV_OVERRIDES = {
    "环境切换 2: 在 .venv312 里运行": {"UV_PROJECT_ENVIRONMENT": ".venv312"},
    "环境切换 3: 往 .venv312 里装包 (pip install requests)": {"UV_PROJECT_ENVIRONMENT": ".venv312"},
}


def command_info(entry):
    label = entry["label"]
    meta = META.get(label, {})
    desc = meta.get("desc") or (label.split("  ", 1)[1] if "  " in label else "")
    prereq = meta.get("prereq", "")
    params = dict(meta.get("params") or {})
    for a in entry["args"]:
        for tok in re.findall(r"<[^>]+>", a):
            params.setdefault(tok, tok[1:-1])
    return desc, prereq, params


def save_json(path, data):
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        print(f"保存失败 {path}: {exc}")


def _classify(path, project):
    p = str(path).lower()
    if project:
        return "项目"
    if "uv\\python" in p or "\\.local\\bin\\" in p or "/.local/bin/" in p:
        return "uv 安装"
    return "系统"


def discover_interpreters():
    """返回 [(显示文本, python.exe 路径, 来源, uv名称), ...]，按 项目 / uv 安装 / 系统 分组排序。"""
    proj, uv_list, sys_list = [], [], []
    seen = set()
    for py in sorted(PROJECT_ROOT.glob(".venv*/Scripts/python.exe")):
        p = str(py)
        proj.append((f"{py.parent.parent.name}   {p}", p, "项目", ""))
        seen.add(p)
    try:
        res = subprocess.run(
            ["uv", "python", "list"], capture_output=True, text=True, timeout=20
        )
        for line in res.stdout.splitlines():
            parts = re.split(r"\s{2,}", line.strip())
            if len(parts) < 2:
                continue
            name, path = parts[0], parts[-1].strip()
            if "<download" in path or not path.lower().endswith(".exe"):
                continue
            if path in seen:
                continue
            seen.add(path)
            if _classify(path, False) == "系统":
                sys_list.append((f"{name}   {path}", path, "系统", name))
            else:
                uv_list.append((f"{name}   {path}", path, "uv 安装", name))
    except Exception:
        pass
    return proj + uv_list + sys_list


def default_interpreter(settings):
    """优先用持久化的解释器，否则回退到项目 .venv 的 python。"""
    interp = settings.get("interpreter")
    if interp and Path(interp).exists():
        return interp
    fallback = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    if fallback.exists():
        return str(fallback)
    return None


class InterpreterDialog(QDialog):
    def __init__(self, parent, entries, current):
        super().__init__(parent)
        self.setWindowTitle("选择 Python 解释器")
        self.resize(600, 400)
        self.selected = current
        self.entries = entries
        layout = QVBoxLayout(self)
        tip = QLabel("选择默认激活的解释器，手动输入框将用它执行命令（也可选「uv 自动选择」）。")
        tip.setWordWrap(True)
        layout.addWidget(tip)
        self.list = QListWidget()
        self.list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self._on_context_menu)

        self._insert_entries()
        if current:
            for i in range(self.list.count()):
                if self.list.item(i).data(Qt.ItemDataRole.UserRole) == current:
                    self.list.setCurrentRow(i)
                    break
        else:
            self.list.setCurrentRow(0)
        layout.addWidget(self.list)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _accept(self):
        item = self.list.currentItem()
        if item is not None:
            self.selected = item.data(Qt.ItemDataRole.UserRole)
        self.accept()

    def _insert_entries(self):
        GROUP_LABELS = {"项目": "项目解释器", "uv 安装": "uv 安装", "系统": "系统安装"}

        def add_header(label):
            h = QListWidgetItem(f"── {label} ──")
            h.setFlags(Qt.ItemFlag.ItemIsEnabled)
            h.setForeground(QBrush(QColor(0x569cd6)))
            self.list.addItem(h)

        none_item = QListWidgetItem("使用 uv 自动选择（不固定解释器）")
        none_item.setData(Qt.ItemDataRole.UserRole, "")
        self.list.addItem(none_item)

        current_group = None
        number = 0
        for display, path, src, uvname in self.entries:
            if src != current_group:
                current_group = src
                number = 0
                add_header(GROUP_LABELS.get(src, src))
            number += 1
            item = QListWidgetItem(f"{number}. {display}")
            item.setData(Qt.ItemDataRole.UserRole, path)
            item.setData(Qt.ItemDataRole.UserRole + 1, src)
            item.setData(Qt.ItemDataRole.UserRole + 2, uvname)
            self.list.addItem(item)

    def _rebuild(self):
        current = self.selected
        self.list.blockSignals(True)
        self.list.clear()
        self._insert_entries()
        if current:
            for i in range(self.list.count()):
                if self.list.item(i).data(Qt.ItemDataRole.UserRole) == current:
                    self.list.setCurrentRow(i)
                    break
        else:
            self.list.setCurrentRow(0)
        self.list.blockSignals(False)

    def _on_context_menu(self, pos):
        idx = self.list.indexAt(pos)
        if not idx.isValid():
            return
        item = self.list.item(idx.row())
        src = item.data(Qt.ItemDataRole.UserRole + 1)
        if not src:
            return
        uvname = item.data(Qt.ItemDataRole.UserRole + 2)
        menu = QMenu(self)
        if uvname:
            act = menu.addAction("卸载此解释器")
        else:
            act = menu.addAction("无法卸载")
            act.setEnabled(False)
            menu.exec(self.list.viewport().mapToGlobal(pos))
            return
        chosen = menu.exec(self.list.viewport().mapToGlobal(pos))
        if chosen == act:
            self._uninstall(idx.row(), item, src, uvname)

    def _uninstall(self, row, item, src, uvname):
        answer = QMessageBox.question(
            self, "卸载解释器",
            f"确定卸载该解释器？\n{uvname}\n（{src}，路径: {item.data(Qt.ItemDataRole.UserRole)}）",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            res = subprocess.run(
                ["uv", "python", "uninstall", uvname],
                capture_output=True, text=True, timeout=120,
            )
            out = (res.stdout or "").strip() or (res.stderr or "").strip()
            if res.returncode == 0:
                QMessageBox.information(self, "卸载解释器", f"卸载成功。\n{out}")
                self.entries = discover_interpreters()
                self._rebuild()
            else:
                QMessageBox.warning(self, "卸载解释器", f"卸载失败：\n{out or res.returncode}")
        except Exception as exc:
            QMessageBox.warning(self, "卸载解释器", f"卸载出错：{exc}")


class CommandEditDialog(QDialog):
    def __init__(self, parent=None, label="", cmd=""):
        super().__init__(parent)
        self.setWindowTitle("uv 命令")
        self.resize(480, 120)
        form = QFormLayout(self)
        self.label_edit = QLineEdit(label)
        self.cmd_edit = QLineEdit(cmd)
        self.cmd_edit.setPlaceholderText("例如: add PySide6 / sync / lock --upgrade")
        form.addRow("名称:", self.label_edit)
        form.addRow("命令(uv 后的参数):", self.cmd_edit)
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)

    def values(self):
        label = self.label_edit.text().strip()
        cmd = self.cmd_edit.text().strip()
        args = shlex.split(cmd) if cmd else []
        return label, args


class StarDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        view = option.widget
        if not isinstance(view, FavListWidget):
            return
        row = index.row()
        fav = view.owner.is_favorite_at(row)
        hovered = row == view.hovered_row
        if not fav and not hovered:
            return
        star_over = hovered and view.hover_star
        if star_over:
            star = "\u2606" if fav else "\u2605"
        else:
            star = "\u2605" if fav else "\u2606"
        painter.save()
        painter.setPen(QColor(0xffb800))
        font = option.font
        font.setPointSize(14)
        painter.setFont(font)
        rect = option.rect
        painter.drawText(rect.adjusted(0, 0, -8, 0),
                         Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                         star)
        painter.restore()


class FavListWidget(QListWidget):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.hovered_row = -1
        self.hover_star = False
        self.setMouseTracking(True)
        self.setItemDelegate(StarDelegate(owner))
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def _on_context_menu(self, pos):
        idx = self.indexAt(pos)
        if not idx.isValid():
            return
        row = idx.row()
        self.setCurrentRow(row)
        entry = self.owner.display[row]
        cmd_text = "uv " + " ".join(entry["args"])
        menu = QMenu(self)
        act_run = menu.addAction("运行")
        act_copy = menu.addAction("复制命令")
        act_fav = menu.addAction(
            "取消收藏" if entry["label"] in self.owner.favorites else "收藏"
        )
        chosen = menu.exec(self.viewport().mapToGlobal(pos))
        if chosen == act_run:
            self.owner.run_selected()
        elif chosen == act_copy:
            QApplication.clipboard().setText(cmd_text)
            self.owner.output.appendPlainText(f"已复制命令: {cmd_text}")
        elif chosen == act_fav:
            self.owner.toggle_favorite_at(row)

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        idx = self.indexAt(pos)
        row = idx.row() if idx.isValid() else -1
        star = False
        if idx.isValid():
            rect = self.visualRect(idx)
            star = pos.x() >= rect.right() - 26
        if row != self.hovered_row or star != self.hover_star:
            self.hovered_row = row
            self.hover_star = star
            self.viewport().update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.hovered_row = -1
        self.hover_star = False
        self.viewport().update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        pos = event.position().toPoint()
        idx = self.indexAt(pos)
        if idx.isValid():
            rect = self.visualRect(idx)
            if pos.x() >= rect.right() - 26:
                self.owner.toggle_favorite_at(idx.row())
                return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        idx = self.indexAt(event.position().toPoint())
        if idx.isValid():
            self.setCurrentRow(idx.row())
            self.owner.run_selected()


class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 uv 命令启动器")
        self.settings = load_json(SIZE_FILE, {})
        width = int(self.settings.get("width", 800))
        height = int(self.settings.get("height", 600))
        self.resize(width, height)
        self.interpreter = default_interpreter(self.settings)

        self.favorites = set(load_json(FAV_FILE, {}).get("favorites", []))
        self.custom = load_json(CUSTOM_FILE, [])
        self.all_commands = [
            {"label": label, "args": args, "builtin": True,
             "env": ENV_OVERRIDES.get(label)} for label, args in BUILTIN
        ] + self.custom
        self.filter_text = ""
        self.display = []
        self.running_row = None
        self.start_time = None

        central = QWidget()
        root = QVBoxLayout(central)
        root.setSpacing(8)

        self.header = QLabel()
        self.header.setWordWrap(True)
        self.header.setTextFormat(Qt.TextFormat.RichText)
        self.header.setStyleSheet("color: #999;")
        root.addWidget(self.header)

        top = QHBoxLayout()
        self.interp_btn = QPushButton("选择解释器")
        self.interp_btn.clicked.connect(self.choose_interpreter)
        self.manual_input = QLineEdit()
        self.manual_input.returnPressed.connect(self.run_manual)
        self.manual_btn = QPushButton("运行")
        self.manual_btn.clicked.connect(self.run_manual)
        self.search = QLineEdit()
        self.search.setPlaceholderText("搜索命令…")
        self.search.textChanged.connect(self._on_search)
        top.addWidget(self.interp_btn)
        top.addWidget(self.manual_input, 2)
        top.addWidget(self.manual_btn)
        top.addWidget(self.search, 2)
        root.addLayout(top)

        self._refresh_header()
        self._refresh_manual_placeholder()

        mid = QHBoxLayout()

        self.detail = QLabel("（未选择命令）")
        self.detail.setWordWrap(True)
        self.detail.setStyleSheet(
            "background:#2d2d2d; border:1px solid #3c3c3c; border-radius:4px;"
            "padding:6px; color:#d4d4d4;"
        )
        self.detail.setFixedWidth(240)
        self.detail.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        mid.addWidget(self.detail)

        self.list = FavListWidget(self)
        self.list.setMinimumWidth(360)
        self.list.currentItemChanged.connect(self._update_fav_btn)
        self.list.currentItemChanged.connect(self._update_detail)
        mid.addWidget(self.list, 1)

        btn_col = QVBoxLayout()
        self.run_btn = QPushButton("运行所选")
        self.run_btn.clicked.connect(self.run_selected)
        self.fav_btn = QPushButton("收藏")
        self.fav_btn.clicked.connect(self.toggle_favorite)
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop)
        self.new_btn = QPushButton("新增命令")
        self.new_btn.clicked.connect(self.add_command)
        self.edit_btn = QPushButton("编辑/删除")
        self.edit_btn.clicked.connect(self.edit_command)
        self.restart_btn = QPushButton("重启程序")
        self.restart_btn.clicked.connect(self.restart)
        for b in (self.run_btn, self.fav_btn, self.stop_btn,
                  self.new_btn, self.edit_btn, self.restart_btn):
            btn_col.addWidget(b)
        btn_col.addStretch(1)
        mid.addLayout(btn_col)

        root.addLayout(mid)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.output.setFont(QFont("Consolas", 10))

        log_row = QHBoxLayout()
        log_btns = QVBoxLayout()
        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self.output.clear)
        log_btns.addWidget(self.clear_btn)
        log_btns.addStretch(1)
        log_row.addWidget(self.output, 1)
        log_row.addLayout(log_btns)
        root.addLayout(log_row, 1)

        self.setCentralWidget(central)

        self.proc = QProcess(self)
        self.proc.setWorkingDirectory(str(PROJECT_ROOT))
        self.proc.readyReadStandardOutput.connect(self._read_stdout)
        self.proc.readyReadStandardError.connect(self._read_stderr)
        self.proc.finished.connect(self._on_finished)

        self.rebuild_list()

    # --- 解释器选择 ---
    def _interp_display(self):
        if not self.interpreter:
            return "uv 自动选择"
        return self.interpreter

    def _refresh_header(self):
        self.header.setText(
            f"项目根目录: {PROJECT_ROOT}<br>"
            f"虚拟环境: {VENV_DIR}<br>"
            f"当前解释器: {self._interp_display()}"
        )

    def _refresh_manual_placeholder(self):
        if self.interpreter:
            self.manual_input.setPlaceholderText(
                "输入参数(用所选解释器执行)，如 -c print(1) / script.py / -m pip list，回车或点「运行」"
            )
        else:
            self.manual_input.setPlaceholderText(
                "手动输入命令 (uv 后的参数，如 sync / add requests)，回车或点「运行」"
            )

    def _save_settings(self):
        save_json(SIZE_FILE, {
            "width": self.width(),
            "height": self.height(),
            "interpreter": self.interpreter or "",
        })

    def choose_interpreter(self):
        entries = discover_interpreters()
        if not entries:
            self.output.appendPlainText("未找到已安装的 Python 解释器（可先在列表中运行 uv python install）。")
            return
        dlg = InterpreterDialog(self, entries, self.interpreter)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        self.interpreter = dlg.selected or None
        self._save_settings()
        self._refresh_header()
        self._refresh_manual_placeholder()
        if self.interpreter:
            self.output.appendPlainText(f"已选择默认解释器: {self.interpreter}")
        else:
            self.output.appendPlainText("已恢复为 uv 自动选择解释器。")

    # --- 列表构建 / 过滤 / 收藏 ---
    def _on_search(self, text):
        self.filter_text = text.strip().lower()
        self.rebuild_list()

    def rebuild_list(self):
        filtered = [c for c in self.all_commands
                    if self.filter_text in c["label"].lower()]
        favorited = [c for c in filtered if c["label"] in self.favorites]
        others = [c for c in filtered if c["label"] not in self.favorites]
        self.display = favorited + others
        self.list.clear()
        for c in self.display:
            item = self.list.addItem(c["label"])
            self.list.item(self.list.count() - 1).setToolTip(self._tooltip(c))
        self._update_fav_btn()
        self._update_detail()

    def _tooltip(self, entry):
        desc, prereq, params = command_info(entry)
        lines = [f"命令: uv {' '.join(entry['args'])}"]
        if desc:
            lines.append(f"说明: {desc}")
        if params:
            lines.append("参数: " + ", ".join(f"{k}={v}" for k, v in params.items()))
        if prereq:
            lines.append(f"前提: {prereq}")
        return "\n".join(lines)

    def _update_detail(self, *_):
        item = self.list.currentItem()
        if item is None:
            self.detail.setText("（未选择命令）")
            return
        entry = self.display[self.list.row(item)]
        desc, prereq, params = command_info(entry)
        text = f"<b>uv {' '.join(entry['args'])}</b>"
        if desc:
            text += f"<br>说明: {desc}"
        if params:
            text += "<br>参数: " + ", ".join(f"{k}={v}" for k, v in params.items())
        if prereq:
            text += f"<br><span style='color:#ff6b6b'>前提: {prereq}</span>"
        self.detail.setText(text)

    def is_favorite_at(self, row):
        return self.display[row]["label"] in self.favorites

    def toggle_favorite_at(self, row):
        label = self.display[row]["label"]
        if label in self.favorites:
            self.favorites.discard(label)
            msg = f"已取消收藏: {label}"
        else:
            self.favorites.add(label)
            msg = f"已收藏(置顶): {label}"
        save_json(FAV_FILE, {"favorites": sorted(self.favorites)})
        self.rebuild_list()
        self.output.appendPlainText(msg)

    def toggle_favorite(self):
        item = self.list.currentItem()
        if item is None:
            QMessageBox.information(self, "收藏", "请先选择一条命令。")
            return
        self.toggle_favorite_at(self.list.row(item))

    def _update_fav_btn(self, *_):
        item = self.list.currentItem()
        if item is None:
            self.fav_btn.setText("收藏")
            return
        label = self.display[self.list.row(item)]["label"]
        self.fav_btn.setText("取消收藏" if label in self.favorites else "收藏")

    # --- 自定义命令 ---
    def add_command(self):
        dlg = CommandEditDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        label, args = dlg.values()
        if not label or not args:
            QMessageBox.warning(self, "新增命令", "名称和命令都不能为空。")
            return
        entry = {"label": label, "args": args}
        self.custom.append(entry)
        self.all_commands.append(entry)
        self._save_custom()
        self.rebuild_list()

    def edit_command(self):
        item = self.list.currentItem()
        if item is None:
            return
        row = self.list.row(item)
        cmd = self.display[row]
        if cmd.get("builtin"):
            QMessageBox.information(self, "编辑", "内置命令不可编辑，可「新增命令」创建自定义项。")
            return
        dlg = CommandEditDialog(self, label=cmd["label"], cmd=" ".join(cmd["args"]))
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        answer = QMessageBox.question(
            self, "编辑/删除",
            f"对「{cmd['label']}」：\n[Yes]=保存修改  [No]=删除  [Cancel]=取消",
        )
        if answer == QMessageBox.StandardButton.Yes:
            label, args = dlg.values()
            if not label or not args:
                QMessageBox.warning(self, "编辑", "名称和命令都不能为空。")
                return
            cmd["label"] = label
            cmd["args"] = args
            self._save_custom()
        elif answer == QMessageBox.StandardButton.No:
            self.custom.remove(cmd)
            self.all_commands.remove(cmd)
            self._save_custom()
        else:
            return
        self.rebuild_list()

    def _save_custom(self):
        save_json(CUSTOM_FILE, [{"label": c["label"], "args": c["args"]} for c in self.custom])

    # --- 参数解析 ---
    def resolve_params(self, args):
        tokens = sorted({t for a in args for t in re.findall(r"<[^>]+>", a)})
        if not tokens:
            return list(args)
        repl = {}
        for tok in tokens:
            name = tok[1:-1]
            val, ok = QInputDialog.getText(self, "参数", f"请输入 {name} 的值:", text=name)
            if not ok:
                return None
            repl[tok] = val
        return [self._replace(a, repl) for a in args]

    @staticmethod
    def _replace(a, repl):
        for tok, val in repl.items():
            a = a.replace(tok, val)
        return a

    # --- 运行 ---
    def run_selected(self):
        item = self.list.currentItem()
        if item is None:
            self.output.appendPlainText("请先选择一个命令。")
            return
        row = self.list.row(item)
        cmd = self.display[row]
        if self.proc.state() != QProcess.ProcessState.NotRunning:
            self.output.appendPlainText("另一个命令正在运行，请稍候（或点「停止」）。")
            return
        args = self.resolve_params(cmd["args"])
        if args is None:
            return
        self._start("uv", args, cmd["label"], row, cmd.get("env"))

    def run_manual(self):
        text = self.manual_input.text().strip()
        if not text:
            self.output.appendPlainText("请输入要运行的命令。")
            return
        if self.proc.state() != QProcess.ProcessState.NotRunning:
            self.output.appendPlainText("另一个命令正在运行，请稍候（或点「停止」）。")
            return
        try:
            args = shlex.split(text)
        except ValueError as exc:
            self.output.appendPlainText(f"命令解析失败: {exc}")
            return
        program = self.interpreter or "uv"
        if not self.interpreter:
            if args and args[0].lower() == "uv":
                args = args[1:]
            if not args:
                self.output.appendPlainText("请输入 uv 之后的参数，例如: sync")
                return
        self._start(program, args, "手动输入", None)

    def _start(self, program, args, label, row, env=None):
        shown = f"$ {program} {' '.join(args)}   ({label})"
        if env:
            shown += "   [" + " ".join(f"{k}={v}" for k, v in env.items()) + "]"
        self.output.appendPlainText(shown + "\n")
        self.start_time = time.monotonic()
        self.running_row = row
        if row is not None:
            self.list.item(row).setForeground(QBrush(QColor(0x0055cc)))
        self.run_btn.setText("运行中…")
        pe = QProcessEnvironment.systemEnvironment()
        for k, v in (env or {}).items():
            pe.insert(k, v)
        self.proc.setProcessEnvironment(pe)
        self.proc.start(program, args)

    def stop(self):
        if self.proc.state() != QProcess.ProcessState.NotRunning:
            self.proc.kill()
            self.output.appendPlainText("已请求停止。")

    def restart(self):
        if self.proc.state() != QProcess.ProcessState.NotRunning:
            self.proc.kill()
        ok = QProcess.startDetached(
            "uv", ["run", "python", "-m", "l_pyside6_uv.main"], str(PROJECT_ROOT)
        )
        if not ok:
            QMessageBox.warning(self, "重启", "无法启动新实例（uv 不在 PATH？），本次不退出。")
            return
        QApplication.instance().quit()

    def closeEvent(self, event):
        self._save_settings()
        super().closeEvent(event)

    def _read_stdout(self):
        data = bytes(self.proc.readAllStandardOutput()).decode("utf-8", "replace")
        self.output.appendPlainText(data.rstrip())

    def _read_stderr(self):
        data = bytes(self.proc.readAllStandardError()).decode("utf-8", "replace")
        self.output.appendPlainText(data.rstrip())

    def _on_finished(self, code, status):
        elapsed = (time.monotonic() - self.start_time) if self.start_time else 0.0
        color = "#0a0" if code == 0 else "#c00"
        self.output.appendHtml(
            f'<span style="color:{color}">=== 结束, exit code: {code}, 耗时 {elapsed:.1f}s ===</span>\n'
        )
        if self.running_row is not None and self.running_row < self.list.count():
            self.list.item(self.running_row).setForeground(QBrush())
        self.running_row = None
        self.start_time = None
        self.run_btn.setText("运行所选")


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_QSS)
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
