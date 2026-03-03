Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """" & WshShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\System.bat""", 0, False