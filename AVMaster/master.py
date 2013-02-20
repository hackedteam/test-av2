import argparse
import sys
import os
import string
from time import sleep
from ConfigParser import ConfigParser
from multiprocessing import Pool

from lib.VMachine import VMachine
from lib.VMManager import VMManagerVS
#from lib.logger import logger
import lib.logger

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
                test_dir = "C:\\Users\\avtest\\Desktop\\AVTEST"
                lib_dir = "%s\\lib" % test_dir
                assets_dir = "%s\\assets" % test_dir
                vmavtest = "../VMAVTest/"

                build_silent_script_src = "../VMAVTest/build_silent_minotauro.bat"
                build_silent_script_dst = "c:\\Users\\avtest\\Desktop\\AVTEST\\build_silent_minotauro.bat"

                vmman.mkdirInGuest(vm, test_dir)

                filestocopy =[  "./build_silent_minotauro.bat",
                                "lib/ConsoleAPI.py", 
                                "lib/vmavtest.py",
                                "lib/logger.py",
                                "lib/rcs_client.py",
                                "assets/config.json",
                                "assets/keyinject.exe",
                                "assets/meltapp.exe"    ]
                memo = []
                for filetocopy in filestocopy:
                        d,f = filetocopy.split("/")
                        src = "%s/%s/%s" % (vmavtest,d,f)

                        if d == ".":
                                dst =  "%s\\%s" % (test_dir,f)
                        else:
                                dst =  "%s\\%s\\%s" % (test_dir,d,f)
                                rdir = "%s\\%s" % (test_dir,d)
                                if not memo.__contains__(rdir):
                                        vmman.mkdirInGuest( vm, rdir )
                                        memo.append( rdir )

                        print src, dst
                        vmman.copyFileToGuest(vm, src, dst)
                #sys.exit(0)

                '''

                api_py_src = "../VMAVTest/lib/ConsoleAPI.py"
                api_py_dst = "c:\\Users\\avtest\\Desktop\\AVTEST\\lib\\ConsoleAPI.py"

                vmavtest_py_src = "../VMAVTest/lib/vmavtest.py"
                vmavtest_py_dst = "c:\\Users\\avtest\\Desktop\\AVTEST\\lib\\vmavtest.py"

                vmavtest_py_src = "../VMAVTest/lib/logger.py"
                vmavtest_py_dst = "c:\\Users\\avtest\\Desktop\\AVTEST\\lib\\logger.py"

                vmavtest_py_src = "../VMAVTest/lib/rcs_client.py"
                vmavtest_py_dst = "c:\\Users\\avtest\\Desktop\\AVTEST\\lib\\rcs_client.py"

                config_json_src = "../VMAVTest/assets/config.json"
                config_json_dst = "c:\\Users\\avtest\\Desktop\\AVTEST\\assets\\config.json"

                keyinject_src = "../VMAVTest/assets/keyinject.exe"
                keyinject_dst = "c:\\Users\\avtest\\Desktop\\AVTEST\\assets\\keyinject.exe"

                meltapp_src = "../VMAVTest/assets/meltapp.exe"
                meltapp_dst = "c:\\Users\\avtest\\Desktop\\AVTEST\\assets\\meltapp.exe"


                # make directories where push scripts for tests
                vmman.mkdirInGuest(vm, test_dir)
                vmman.mkdirInGuest(vm, lib_dir)
                vmman.mkdirInGuest(vm, assets_dir)

                # copy files
                vmman.copyFileToGuest(vm, build_silent_script_src, build_silent_script_dst)
                vmman.copyFileToGuest(vm, api_py_src, api_py_dst)
                vmman.copyFileToGuest(vm, vmavtest_py_src, vmavtest_py_dst)
                vmman.copyFileToGuest(vm, config_json_src, config_json_dst)
                vmman.copyFileToGuest(vm, keyinject_src, keyinject_dst)
                 vmman.copyFileToGuest(vm, meltapp_src, meltapp_dst)
                '''
                # executing bat
                vmman.executeCmd(vm, build_silent_script_dst)
                
                # suspend & refresh snapshot
                #vmman.suspend(vm)
                #sleep(5)
                #vmman.refreshSnapshot(vm, vm.snapshot)
                
                return "[*] test files dispatched for %s" % vm_name

        except Exception, ex:
                print "exception inside ", ex
                return "Error: cannot dispatch tests for %s" % vm_name

def main():
        lib.logger.setLogger()
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
