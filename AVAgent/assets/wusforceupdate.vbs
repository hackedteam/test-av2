'
' NAME : <wusforceupdate>
' AUTHOR : <Samuel lambert>
' COMMENT : <Find-Download-Install-reboot (with windows update system WUS)>
' www.wsus.info/forums/lofiversion/index.php?t5454.html

'Shutdown flags;
 const nLog_Off          =  0 
 const nForced_Log_Off   =  4  '( 0 + 4 ) 
 const nShutdown         =  1
 const nForced_Shutdown  =  5  '( 1 + 4 ) 
 const nReboot           =  2
 const nForced_Reboot    =  6  '( 2 + 4 )
 const nPower_Off        =  8
 const nForced_Power_Off = 12  '( 8 + 4 )

ShutdownOption = nForced_Reboot

'Monthly log;
dt = date() : nMonth = Year(dt)*1e2 + Month(dt)
sLogFile = "C:\WUSforceupdate-" & nMonth & ".log"


Set updateSession = CreateObject("Microsoft.Update.Session")
Set updateSearcher = updateSession.CreateupdateSearcher()

Set searchResult = _
updateSearcher.Search("IsInstalled=0 and Type='Software'")

Set File = CreateObject("Scripting.FileSystemObject")
Set LogFile = File.OpenTextFile(sLogFile, 8, True)

LogFile.WriteLine("***************************************************************")
LogFile.WriteLine( "START TIME : " & now)
LogFile.WriteLine( "Searching for updates..." & vbCRLF)
LogFile.WriteLine( "List of applicable items on the machine:")

For I = 0 To searchResult.Updates.Count-1
  Set update = searchResult.Updates.Item(I)
  LogFile.WriteLine( I + 1 & "> " & update.Title)
Next

Set WshShell = WScript.CreateObject("WScript.Shell")

If searchResult.Updates.Count = 0 Then
  LogFile.WriteLine( "There are no applicable updates.")
  WshShell.popup "There are no applicable updates.",1
  ShutDown(ShutdownOption)  '<-- O P T I O N A L
  Wscript.quit
End If

LogFile.WriteLine( vbCRLF & "Creating collection of updates to download:")

Set updatesToDownload = CreateObject("Microsoft.Update.UpdateColl")

For I = 0 to searchResult.Updates.Count-1
  Set update = searchResult.Updates.Item(I)
  LogFile.WriteLine( I + 1 & "> adding: " & update.Title )
  updatesToDownload.Add(update)
Next

LogFile.WriteLine( vbCRLF & "Downloading updates...")

Set downloader = updateSession.CreateUpdateDownloader() 
downloader.Updates = updatesToDownload
downloader.Download()

LogFile.WriteLine( vbCRLF & "List of downloaded updates:")

For I = 0 To searchResult.Updates.Count-1
  Set update = searchResult.Updates.Item(I)
  If update.IsDownloaded Then
    LogFile.WriteLine( I + 1 & "> " & update.Title )
  End If
Next

Set updatesToInstall = CreateObject("Microsoft.Update.UpdateColl")

LogFile.WriteLine( vbCRLF & _
   "Creating collection of downloaded updates to install:" )

For I = 0 To searchResult.Updates.Count-1
  set update = searchResult.Updates.Item(I)
  If update.IsDownloaded = true Then
    'WshShell.popup "installing..." & vbNewLine & update.Title,1
    LogFile.WriteLine( I + 1 & "> adding: " & update.Title )
    updatesToInstall.Add(update) 
  End If
Next

logFile.WriteLine( "Installing updates...")
Set installer = updateSession.CreateUpdateInstaller()
installer.Updates = updatesToInstall
Set installationResult = installer.Install()

'Output results of install
LogFile.WriteLine( "Installation Result: " & installationResult.ResultCode )
LogFile.WriteLine( "Reboot Required: " & installationResult.RebootRequired & vbCRLF )

LogFile.WriteLine( "Listing of updates installed " _
    & "and individual installation results:" )

For I = 0 to updatesToInstall.Count - 1
  LogFile.WriteLine( I + 1 & "> " & updatesToInstall.Item(i).Title _ 
    & ": " & installationResult.GetUpdateResult(i).ResultCode ) 
Next

If installationResult.RebootRequired = -1 then
  LogFile.WriteLine( "RebootRequired")
  ' <-- normally now you should call for a R E B O O T.....
End if

ShutDown(ShutdownOption)  '<-- O P T I O N A L

LogFile.WriteLine( "STOP TIME : " & now)
LogFile.WriteLine("***************************************************************")
LogFile.Close

wscript.echo "Updates are installed"


Function ShutDown(sFlag)
 wscript.sleep 600
  Set OScoll = GetObject( _
     "winmgmts:{(Shutdown)}").ExecQuery( _
     "Select * from Win32_OperatingSystem") 
  For Each osObj in OScoll
    osObj.Win32Shutdown(sFlag)
  Next
End Function