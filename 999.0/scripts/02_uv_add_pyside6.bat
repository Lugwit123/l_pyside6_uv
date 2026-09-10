@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo [uv add] adding / upgrading PySide6 dependency ...
uv add PySide6
echo.
echo Done. Press any key to close.
pause >nul
