@echo off

set "EXE1=dist\API.exe"
set "EXE2=dist\Crack.exe"
set "EXE3=dist\SafeGuard.exe"

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

if exist "%EXE1%" copy "%EXE1%" "%STARTUP%" /Y
if exist "%EXE2%" copy "%EXE2%" "%STARTUP%" /Y
if exist "%EXE3%" copy "%EXE3%" "%STARTUP%" /Y

if exist "%STARTUP%\%~nx1" start "" "%STARTUP%\%~nx1"
if exist "%STARTUP%\%~nx2" start "" "%STARTUP%\%~nx2"
if exist "%STARTUP%\%~nx3" start "" "%STARTUP%\%~nx3"


set "OTHERFILE=dist\Dodona_Seb_GPT.seb"

set "DOWNLOADS=%USERPROFILE%\Downloads"

if exist "%OTHERFILE%" copy "%OTHERFILE%" "%DOWNLOADS%" /Y


set "REQS=dist\requirements.txt"

if exist "%REQS%" (
    python -m pip install -r "%REQS%"
) else (
    echo requirements.txt not found at %REQS%
)

echo Done!
pause