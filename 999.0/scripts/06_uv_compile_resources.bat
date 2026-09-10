@echo off
chcp 65001 >nul
cd /d "%~dp0.."
if not exist "resources\*.qrc" (
    echo No .qrc files found in resources\ folder. Put resource files there first.
    goto :end
)
for %%f in (resources\*.qrc) do (
    echo compiling %%f -^> src\l_pyside6_uv\resources_%%~nf_rc.py
    uv run pyside6-rcc "%%f" -o "src\l_pyside6_uv\resources_%%~nf_rc.py"
)
:end
echo.
echo Done. Press any key to close.
pause >nul
