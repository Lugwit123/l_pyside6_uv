@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo [uv run] starting PySide6 app ...
uv run python -m l_pyside6_uv.main
echo.
echo App exited. Press any key to close.
pause >nul
