import sys
from threading import Thread

from VMachine import VMachine
from VMManager import VMManagerFus

class Task(Thread):
    
    def __init__(self, vm, exe_path, vmrun_path):
        Thread.__init__(self)
        self.vm = vm
        self.exe_path = exe_path
        self.vmrun_path = vmrun_path
        
    def run(self):
        exe_path_dst = "c:\\Users\\avtest\\Desktop\\arg.exe"


        vmman = VMManagerFus(self.vmrun_path)
        
        # 0. revert to snapshot
        vmman.revertSnapshot(self.vm)
        
        # 1. startup vm
        vmman.startup(self.vm)
        
        # 2. copy file
        vmman.copyFileToGuest(self.vm, self.exe_path, exe_path_dst)
        
        # 3. infection
        c = raw_input("[>] Press Enter to executing infection...\n")
        x = vmman.executeCmd(self.vm, exe_path_dst)

        if x is not True:
            sys.stdout.write("[!] Execution failed\n")
            vmman.shutdown(self.vm)
            sys.exit(0)
        
        # 4. wait for reboot
        c = raw_input("[>] Wait 5 min and reboot (press enter when ok)...\n")
        #sleep(300)
        vmman.reboot(self.vm)
        
        # n. finally shutdown
        c = raw_input("[>] Press enter to end Analysis and shutdown current VM...\n")
        #vmman.shutdown(self.vm)



        

