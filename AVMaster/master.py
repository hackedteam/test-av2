import argparse
import sys
import os
import string
from time import sleep
from ConfigParser import ConfigParser
from multiprocessing import Pool
import argparse
import random

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
            sleep(random.randint(10,60))
            vmman.startup(vm)
            # executing scripts for vm and wait 3 hours
            print "[%s] waiting for Updatess" % vm_name
            sleep(50 * 60)
            sleep(random.randint(10,600))
            print "[%s] Shutdown for reconfigurations" % vm_name
            vmman.shutdown(vm)
            sleep(30 * 60)
            print "[%s] Startup" % vm_name
            vmman.startup(vm)
            sleep(10 * 60)
            print "[%s] Suspending and saving new snapshot" % vm_name
            vmman.suspend(vm)
            sleep(30)
            vmman.refreshSnapshot(vm)
            return "[%s] Updated!"  % vm_name
        except Exception as e:
            return "ERROR: %s is not updated. Reason: %s" % (vm_name, e)


def revert(vm_name):
    vm = VMachine(vm_conf_file, vm_name)
    vmman.revertSnapshot(vm, vm.snapshot)
    sleep(2)
    return "[*] %s reverted!"


def test_internet(vm_name):
    #try:
    vm = VMachine(vm_conf_file, vm_name)

    vmman.revertSnapshot(vm, vm.snapshot)
    sleep(5)
    vmman.startup(vm)
    sleep(60)
    
    test_dir = "C:\\Users\\avtest\\Desktop\\AVTEST"
    lib_dir = "%s\\lib" % test_dir
    assets_dir = "%s\\assets" % test_dir
    vmavtest = "../VMAVTest"
    
    vmman.mkdirInGuest(vm, test_dir)

    filestocopy =[  "./test_internet.bat",
                    "lib/vmavtest.py",
                    "lib/logger.py",
                    "lib/rcs_client.py",
                    "assets/config.json",
                    "assets/keyinject.exe",
                    "assets/meltapp.exe"    ]
    memo = []
    for filetocopy in filestocopy:
        d,f = filetocopy.split("/")

        if d == ".":
            src = "%s/%s" % (vmavtest,f)
            dst =  "%s\\%s" % (test_dir,f)
        else:
            src = "%s/%s/%s" % (vmavtest,d,f)
            dst =  "%s\\%s\\%s" % (test_dir,d,f)
            rdir = "%s\\%s" % (test_dir,d)
            if not memo.__contains__(rdir):
                vmman.mkdirInGuest( vm, rdir )
                memo.append( rdir )

        #print src, dst
        vmman.copyFileToGuest(vm, src, dst)
    
    # executing bat synchronized
    vmman.executeCmd(vm, "%s\\test_internet.bat" % test_dir)
    return "[%s] dispatched test internet" % vm_name
 

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
                                "lib/vmavtest.py",
                                "lib/logger.py",
                                "lib/rcs_client.py",
                                "assets/config.json",
                                "assets/keyinject.exe",
                                "assets/meltapp.exe"    ]
                memo = []
                for filetocopy in filestocopy:
                        d,f = filetocopy.split("/")

                        if d == ".":
                            src = "%s/%s" % (vmavtest,f)
                            dst =  "%s\\%s" % (test_dir,f)
                        else:
                            src = "%s/%s/%s" % (vmavtest,d,f)
                            dst =  "%s\\%s\\%s" % (test_dir,d,f)
                            rdir = "%s\\%s" % (test_dir,d)
                            if not memo.__contains__(rdir):
                                    vmman.mkdirInGuest( vm, rdir )
                                    memo.append( rdir )

                        print src, dst
                        vmman.copyFileToGuest(vm, src, dst)

                # executing bat synchronized
                vmman.executeCmd(vm, "%s\\build_silent_minotauro.bat" % test_dir )
                
                # save results.txt locally
                save_results(vm)

                # suspend & refresh snapshot
                vmman.suspend(vm)
                #sleep(5)
                #vmman.refreshSnapshot(vm, vm.snapshot)
                
                return "[%s] test files dispatched" % vm_name

        except Exception, ex:
                print "exception inside ", ex
                return "Error: cannot dispatch tests for %s" % vm_name


def save_results(vm):
    filename = "results.%s.txt" % vm
    vmman.copyFileFromGuest(vm, "c:\\Users\\avtest\\Desktop\\AVTEST\\results.txt", filename)

    last = "Error save"
    f = open(filename, 'rb')
    for l in f.readlines():
        if l.__contains__(" + "):
            last = l

    return "%s %s" % (vm, last)

def main():
        lib.logger.setLogger()

        parser = argparse.ArgumentParser(description='AVMonitor master.')
    
        parser.add_argument('action', choices=['update', 'revert', 'dispatch', 'test', 'test_internet'],
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

        actions = { "update" : update, "revert": revert, 
                    "dispatch": dispatch, "test_internet": test_internet }
        r = pool.map_async(actions[args.action], vm_names)
        print "[*] RESULTS: "
        print r.get()


if __name__ == "__main__":
    #if len(sys.argv) > 1:
    	main()
