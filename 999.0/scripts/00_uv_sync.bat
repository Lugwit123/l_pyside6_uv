@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo [uv sync] installing / syncing dependencies from pyproject.toml ...
uv sync
echo.
echo Done. Press any key to close.
pause >nul
