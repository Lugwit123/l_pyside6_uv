@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo [doctor] checking uv ...
uv --version
if errorlevel 1 goto :fail
echo [doctor] checking PySide6 ...
uv run python -c "import PySide6; print('PySide6', PySide6.__version__)"
if errorlevel 1 goto :fail
echo.
echo [doctor] OK - environment ready.
goto :end
:fail
echo.
echo [doctor] FAILED - run 00_uv_sync.bat first (or check uv install).
:end
echo.
pause >nul
