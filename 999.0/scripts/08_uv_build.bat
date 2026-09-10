@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo [uv build] building wheel / sdist ...
uv build
echo.
echo Done. Output in dist\. Press any key to close.
pause >nul
