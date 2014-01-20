%windir%\system32\wuauclt.exe /DetectNow
%windir%\system32\wuauclt.exe /UpdateNow


@echo "Manual update AV, then press enter"
@pause

%windir%\system32\shutdown.exe /s /f /t 0