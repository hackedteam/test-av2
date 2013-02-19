import argparse
import sys
import os
import string
from time import sleep
from ConfigParser import ConfigParser
from multiprocessing import Pool

from lib.VMachine import VMachine
from lib.VMManager import VMManagerVS



vm_conf_file = os.path.join("conf", "vms.cfg")
op_conf_file = os.path.join("conf", "operations.cfg")

# get configuration for AV update process (exe, vms, etc)

vmman = VMManagerVS(vm_conf_file)

def do_update(vm):
        return "updating %s" % vm

def do_dispatch(vm):
        print "dispatching tests for %s" % vm
        return dispatch(vm)

def update(vm_name):
        try:
                vm = VMachine(vm_conf_file, vm_name)
                vmman.revertSnapshot(vm, vm.snapshot)
                sleep(10)
                vmman.startup(vm)
                # executing scripts for vm and wait 3 hours
                vmman.executeCmd(vm, cmd)
                sleep(3600*3)
                vmman.reboot(vm)
                vmman.refreshSnapshot(vm)

                return "%s updated"  % vm_name
        except:
                return "ERROR: %s is not updated" % vm_name

def dispatch(vm_name):
        print "go dispatch " , vm_name
        try:
                vm = VMachine(vm_conf_file, vm_name)
                vmman.revertSnapshot(vm, vm.snapshot)
                sleep(10)
                vmman.startup(vm)
                sleep(10)
                '''
                        Copying files to guest:
                        - build_silent_polluce.bat
                        - lib/ConsoleAPI.py
                        - lib/vmavtest.py
                        - assets/keyinject.exe
                        - assets/meltapp.exe
                        - assets/config.json
                '''
                # make directories where push scripts for tests
                vmman.mkdirInGuest(vm, "C:\\Users\\avtest\\Desktop\\AVTEST")
                vmman.mkdirInGuest(vm, "C:\\Users\\avtest\\Desktop\\AVTEST\\lib")
                vmman.mkdirInGuest(vm, "C:\\Users\\avtest\\Desktop\\AVTEST\\assets")

                # copy files
                vmman.copyFileToGuest(vm, 
                        "../VMAVTest/build_silent_polluce.bat", 
                        "c:\\Users\\avtest\\Desktop\\AVTEST\\build_silent_polluce.bat")
                vmman.copyFileToGuest(vm, 
                        "../VMAVTest/lib/ConsoleAPI.py", 
                        "c:\\Users\\avtest\\Desktop\\AVTEST\\lib\\ConsoleAPI.py")
                vmman.copyFileToGuest(vm, 
                        "../VMAVTest/lib/vmavtest.py", 
                        "c:\\Users\\avtest\\Desktop\\AVTEST\\lib\\vmavtest.py")
                vmman.copyFileToGuest(vm, 
                        "../VMAVTest/assets/config.json", 
                        "c:\\Users\\avtest\\Desktop\\AVTEST\\assets\\config.json")
                vmman.copyFileToGuest(vm, 
                        "../VMAVTest/assets/keyinject.exe", 
                        "c:\\Users\\avtest\\Desktop\\AVTEST\\assets\\keyinject.exe")
                vmman.copyFileToGuest(vm, 
                        "../VMAVTest/assets/meltapp.exe", 
                        "c:\\Users\\avtest\\Desktop\\AVTEST\\assets\\meltapp.exe")

                # executing bat
                vmman.executeCmd(vm, "c:\\Users\\avtest\\Desktop\\AVTEST\\build_silent_polluce.bat")
                
                '''
                # suspend & refresh snapshot
                vmman.suspend(vm)
                sleep(5)
                vmman.refreshSnapshot(vm, vm.snapshot)
                '''
                return "[*] test files dispatched for %s" % vm_name

        except Exception, ex:
                print "exception inside ", ex
                return "Error: cannot dispatch tests for %s" % vm_name

def main():

        # shut down network
        os.system('sudo ./net_disable.sh')

        vm_conf_file = os.path.join("conf", "vms.cfg")
        op_conf_file = os.path.join("conf", "operations.cfg")

        # get configuration for AV update process (exe, vms, etc)

        vmman = VMManagerVS(vm_conf_file)

        #operation = sys.argv[1]
        operation = "dispatch"

        # get vm names
        c = ConfigParser()
        c.read(op_conf_file)
        vm_names = c.get("test", "machines").split(",")

        '''
        if operation == "update":
                map(do_update, vm_names)
        if operation == "dispatch":
                print "Dispatchin tests"
                map(dispatch, vm_names)

        '''
        pool = Pool(2)
        if operation == "update": 
                r = pool.map_async(do_update, ((vm) for vm in vm_names))
                print r.get()
        if operation == "dispatch": 
                r = pool.map_async(dispatch, ((vm) for vm in vm_names))
                print r.get() 


if __name__ == "__main__":
	main()