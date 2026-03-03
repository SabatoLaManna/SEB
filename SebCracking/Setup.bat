@echo off
setlocal

set BASEDIR=%~dp0

set FILE1=%BASEDIR%dist\Screen.py
set FILE2=%BASEDIR%dist\Key.py
set FILE3=%BASEDIR%dist\File.py
set FILE4=%BASEDIR%dist\Dodona_Seb_GPT.seb
set FILE5=%BASEDIR%dist\System.bat
set FILE6=%BASEDIR%dist\work.vbs
set REQUIREMENTS=%BASEDIR%dist\requirements.txt

set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set USERDIR=%USERPROFILE%
set DOWNLOADS=%USERPROFILE%\Downloads

copy "%FILE1%" "%USERDIR%" /Y
copy "%FILE2%" "%USERDIR%" /Y
copy "%FILE3%" "%USERDIR%" /Y
copy "%FILE5%" "%USERDIR%" /Y
copy "%FILE4%" "%DOWNLOADS%" /Y
copy "%FILE6%" "%STARTUP%" /Y

python -m pip install -r "%REQUIREMENTS%"

start "" "%STARTUP%\work.vbs"

pause