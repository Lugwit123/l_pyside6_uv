@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo [uv run] opening Qt Designer (visual UI editor) ...
uv run pyside6-designer
echo.
echo Designer closed. Press any key to close.
pause >nul
