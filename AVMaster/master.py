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

def update(vm_name):
        try:
            vm = VMachine(vm_conf_file, vm_name)
            vmman.revertSnapshot(vm, vm.snapshot)
            sleep(10)
            vmman.startup(vm)
            # executing scripts for vm and wait 3 hours
            vmman.executeCmd(vm, cmd)
            sys.stdout.write("[%s] waiting for Updates")
            sleep(3600)
            vmman.reboot(vm)
            sys.stdout.write("[%s] waiting for reconfigurations")
            sleep(300)
            #sleep(60)
            vmman.suspend(vm)
            sleep(3)
            vmman.refreshSnapshot(vm)
            return "[%s] Updated!"  % vm_name
        except Exception as e:
            return "ERROR: %s is not updated. Reason: %s" % (vm_name, e)


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
    
        parser.add_argument('action', choices=['update', 'revert', 'dispatch', 'test'],
            help="The operation to perform")
        parser.add_argument('--vm', required=False, 
            help="Virtual Machine where execute the operation")
        parser.add_argument('-p', '--pool', default=2, type=int, 
            help="This is the number of parallel process (default 2)")
        args = parser.parse_args()

        if args.action == "test":
            get_results("eset")
            exit(0)

        # shut down network
        if args.action == "update":
            os.system('sudo ./net_enable.sh')
            print "[!] Enabling NETWORKING!"
        else:
            os.system('sudo ./net_disable.sh')
            print "[!] Disabling NETWORKING!"

        vm_conf_file = os.path.join("conf", "vms.cfg")
        op_conf_file = os.path.join("conf", "operations.cfg")

        # get configuration for AV update process (exe, vms, etc)

        vmman = VMManagerVS(vm_conf_file)

        # get vm names
        c = ConfigParser()
        c.read(op_conf_file)
        vm_names = c.get("test", "machines").split(",")

        pool = Pool(int(args.pool))

        print "[*] selected operation %s" % args.action

        actions = { "update" : update, "revert": revert, "dispatch": dispatch }
        r = pool.map_async(actions[args.action], vm_names)
        print r.get()


if __name__ == "__main__":
    #if len(sys.argv) > 1:
    	main()
