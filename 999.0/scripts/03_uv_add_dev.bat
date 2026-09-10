@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo [uv add --dev] adding dev dependency (example: pyinstaller) ...
echo Edit this script to add your own dev dependencies.
uv add --dev pyinstaller
echo.
echo Done. Press any key to close.
pause >nul
