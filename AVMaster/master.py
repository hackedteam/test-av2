import argparse
import sys
import os
import string
from time import sleep
from ConfigParser import ConfigParser
from multiprocessing import Pool
import argparse

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


def revert(vm_name):
    vm = VMachine(vm_conf_file, vm_name)
    vmman.revertSnapshot(vm, vm.snapshot)
    sleep(2)
    return "[*] %s reverted!"


def dispatch(vm_name):
        print "go dispatch " , vm_name
        try:
                vm = VMachine(vm_conf_file, vm_name)
                vmman.revertSnapshot(vm, vm.snapshot)
                sleep(5)
                vmman.startup(vm)
                sleep(5)

                test_dir = "C:\\Users\\avtest\\Desktop\\AVTEST"
                lib_dir = "%s\\lib" % test_dir
                assets_dir = "%s\\assets" % test_dir
                vmavtest = "../VMAVTest/"

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

                # executing bat synchronized
                vmman.executeCmd(vm, build_silent_script_dst)
                
                # save results.txt locally
                save_results(vm)

                # suspend & refresh snapshot
                vmman.suspend(vm)
                #sleep(5)
                #vmman.refreshSnapshot(vm, vm.snapshot)
                
                return "[*] test files dispatched for %s" % vm_name

        except Exception, ex:
                print "exception inside ", ex
                return "Error: cannot dispatch tests for %s" % vm_name


def save_results(vm):
    vmman.copyFileFromGuest(vm, "c:\\Users\\avtest\\Desktop\\AVTEST\\results.txt", "results.%s.txt" % vm_name)


def main():
        lib.logger.setLogger()

        parser = argparse.ArgumentParser(description='AVMonitor master.')
    
        parser.add_argument('action', choices=['update', 'revert', 'dispatch', 'test'])
        parser.add_argument('--vm', required=False)
        parser.add_argument('-p', '--pool', default=2)
        args = parser.parse_args()

        if args.action == "test":
            get_results("eset")
            exit(0)

        # shut down network
        os.system('sudo ./net_disable.sh')

        vm_conf_file = os.path.join("conf", "vms.cfg")
        op_conf_file = os.path.join("conf", "operations.cfg")

        # get configuration for AV update process (exe, vms, etc)

        vmman = VMManagerVS(vm_conf_file)

        # get vm names
        c = ConfigParser()
        c.read(op_conf_file)
        vm_names = c.get("test", "machines").split(",")

        pool = Pool(args.pool)

        print "[*] selected operation %s" % operation

        actions = { "update" : update, "revert": revert, "dispatch": dispatch }
        r = pool.map_async(action[args.action], vm_names)
        print r.get()


if __name__ == "__main__":
    if len(sys.argv) > 1:
    	main()
