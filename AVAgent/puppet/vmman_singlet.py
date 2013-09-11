import sys
from time import sleep

from VMManager import VMManagerFus
from VMMachine import VMMachine
from ConsoleAPI import API

conf_file = "vms.cfg"
vmrun_path = "/Applications/VMwareFusion.app/Contents/Library/vmrun"

autologin_script = "C:\\Users\\avtest\\Desktop\\autologon.bat"

exe_path_src = "/Users/olli/Documents/work/AVTesting/malware/arg.exe"
exe_path_dst = "c:\\Users\\avtest\\Desktop\\arg.exe"


greet = '''
              _,=(_)=,_
           ,;`         `;,
          \\    (\^/)    //
           \\   <( )>   //
            <`-'`"""`'-`>
           _/           \_
         _(_\           /_)_
        /|` |`----.----`| `|\
        |/  |     |     |  \|
       />   |     |     |   <\
           _;     |     ;_
         <`_\     |     /_`>
         |\  `._  |  _.'  /|
         \|     `"""`    |/
          |\            /|
    jgs    \\          //
           /_>        <_\
'''


#
# Defining VM Manager
#
vmman = VMManagerFus(vmrun_path)

#
# Defining all vms you need
#
avg = VMMachine(conf_file, "avg")


# 0. revert to snapshot
#
vmman.revertSnapshot(avg)
# 1. startup vm
vmman.startup(avg)
#
# 2. copy file
vmman.copyFileToGuest(avg, exe_path_src, exe_path_dst)
#
# 3. infection
c = raw_input("[>] Press Enter to executing infection...\n")
x = vmman.executeCmd(avg, exe_path_dst)

if x is not True:
  sys.stdout.write("[!] Execution failed\n")
  vmman.shutdown(avg)
  sys.exit(0)
#
# 4. wait for reboot
c = raw_input("[>] Wait 5 min and reboot (press enter when ok)...\n")
#sleep(300)
vmman.reboot(avg)
#
# n. finally shutdown
c = raw_input("[>] Press enter to end Analysis and shutdown current VM...\n")
#vmman.shutdown(avg)


