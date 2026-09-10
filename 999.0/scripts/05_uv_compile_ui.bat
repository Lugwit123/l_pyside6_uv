@echo off
chcp 65001 >nul
cd /d "%~dp0.."
if not exist "ui\*.ui" (
    echo No .ui files found in ui\ folder. Put Qt Designer files there first.
    goto :end
)
for %%f in (ui\*.ui) do (
    echo compiling %%f -^> src\l_pyside6_uv\ui_%%~nf.py
    uv run pyside6-uic "%%f" -o "src\l_pyside6_uv\ui_%%~nf.py"
)
:end
echo.
echo Done. Press any key to close.
pause >nul
