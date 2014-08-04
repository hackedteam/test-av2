REGEDIT4

; @ECHO OFF
; CLS
; REGEDIT.EXE /S "%~f0"
; ping 1.1.1.1 -n 1 -w 3000
; LOGOFF
; EXIT

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon]
"ForceAutoLogon"="1"
"AutoAdminLogon"="1"
"DefaultUserName"="avtest"
"DefaultPassword"="avtest"