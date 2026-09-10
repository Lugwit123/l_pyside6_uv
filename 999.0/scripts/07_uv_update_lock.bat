@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo [uv lock] upgrading all dependencies and refreshing lock file ...
uv lock --upgrade
echo.
echo Done. Press any key to close.
pause >nul
