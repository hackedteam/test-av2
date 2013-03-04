import argparse
import os
import time
from time import sleep
from ConfigParser import ConfigParser
from multiprocessing import Pool
import random
import os.path
import sys
import traceback

from lib.VMachine import VMachine
from lib.VMManager import VMManagerVS
#from lib.logger import logger
import lib.logger

vm_conf_file = os.path.join("conf", "vms.cfg")
op_conf_file = os.path.join("conf", "operations.cfg")

# get configuration for AV update process (exe, vms, etc)

logdir = ""
vmman = VMManagerVS(vm_conf_file)

def job_log(vm_name, status):
    print "+ %s: %s" % (vm_name, status)

def update(args):
    try:
        vm_name = args[0]
        vm = VMachine(vm_conf_file, vm_name)
        job_log(vm_name, "UPDATE")

        vmman.revertLastSnapshot(vm)

        job_log(vm_name, "REVERTED")

        sleep(random.randint(10,60))
        vmman.startup(vm)
        job_log(vm_name, "STARTED")

        sleep(5 * 60)
        #vmman.deleteDirectoryInGuest(vm, "/users/avtest/Desktop/avtest")

        if _wait_for_startup(vm) is False:
            job_log(vm_name, "NOT STARTED")
            return "ERROR wait for startup for %s" % vm_name

        out_img = "%s/screenshot_%s_update.png" % (logdir, vm_name)
        vmman.takeScreenshot(vm, out_img)
        print "[%s] waiting for Updates" % vm_name
        sleep(50 * 60)
        sleep(random.randint(10,300))

        running = True
        job_log(vm_name, "SHUTDOWN")
        r = vmman.shutdownUpgrade(vm)

        if r is False:
            return "[%s] NOT Updated!"  % vm_name

        count = 0
        sh = True

        while running == True:
            sleep(60)
            running = vmman.VMisRunning(vm)
            count +=1
            job_log(vm_name, "RUNNING %s" % count)
            if count >= 120:
                sh = False
                break

        if sh == True:
            vmman.refreshSnapshot(vm)
            job_log(vm_name, "UPDATED")
            return "[%s] Updated!"  % vm_name
        else:
            job_log(vm_name, "NOT UPDATED")
            return "[%s] NOT Updated!"  % vm_name

    except Exception as e:
        job_log(vm_name, "ERROR")
        return "ERROR: %s is not updated. Reason: %s" % (vm_name, e)


def revert(vm_name):
    vm = VMachine(vm_conf_file, vm_name)
    vmman.revertSnapshot(vm, vm.snapshot)
    sleep(2)
    return "[*] %s reverted!"

def run_command(args):
    vm_name, cmd = args
    if cmd is None:
        return False
    vmx = VMachine(vm_conf_file, vm_name)
    vmman._run_cmd(vmx, cmd)

    return True

def copy_to_guest(vm, test_dir, filestocopy):
    #lib_dir = "%s\\lib" % test_dir
    #assets_dir = "%s\\assets" % test_dir
    vmavtest = "../VMAVTest"

    memo = []
    for filetocopy in filestocopy:
        d,f = filetocopy.split("/")
        src = "%s/%s/%s" % (vmavtest, d, f)

        if d == ".":
            dst =  "%s\\%s" % (test_dir, f)
        else:
            dst =  "%s\\%s\\%s" % (test_dir, d, f)

        rdir = "%s\\%s" % (test_dir, d)
        if not rdir in memo:
            print "DBG mkdir %s " % (rdir)
            vmman.mkdirInGuest( vm, rdir )
            memo.append( rdir )

        print "DBG copy %s -> %s" % (src, dst)
        vmman.copyFileToGuest(vm, src, dst)

def save_results(vm, kind):
    try:
        filename = "%s/results_%s_%s.txt" % (logdir, vm, kind)
        vmman.copyFileFromGuest(vm, "c:\\Users\\avtest\\Desktop\\AVTEST\\results.txt", filename)

        last = "ERROR save"
        f = open(filename, 'rb')
        for l in f.readlines():
            if " + " in l:
                last = l

        return "%s) %s" % (vm, last)
    except Exception as e:
        return "[%s] ERROR saving results with exception: %s" % (vm,e)

def dispatch(args):
    try:
        vm_name, kind = args
        results = []
        print "DBG %s, %s" %(vm_name,kind)
        if kind == "all":
            results.append("silent, %s" % dispatch_kind(vm_name, "silent") )
            sleep(random.randint(5,10))
            results.append("melt, %s" % dispatch_kind(vm_name, "melt") )
        else:
            results.append("silent, %s" % dispatch_kind(vm_name, kind) )

        return results
    except Exception as e:
        print "ERROR> %s %s" % (kind, e)
        print "DBG trace %s" % traceback.format_exc()
        return {'ERROR': e}

def dispatch_kind(vm_name, kind):
    
    vm = VMachine(vm_conf_file, vm_name)
    job_log(vm_name, "DISPATCH %s" % kind)
    
    vmman.revertLastSnapshot(vm)
    job_log(vm_name, "REVERTED")

    sleep(5)
    vmman.startup(vm)
    sleep(5* 60)
    job_log(vm_name, "STARTUP")
    
    test_dir = "C:\\Users\\avtest\\Desktop\\AVTEST"

    # TODO: pull this value, add a new option
    host = "minotauro"
    #host = "polluce"

    buildbat = "build_%s_%s.bat" % (kind, host)

    filestocopy =[  "./%s" % buildbat,
                    "lib/vmavtest.py",
                    "lib/logger.py",
                    "lib/rcs_client.py",
                    "conf/vmavtest.cfg",
                    "assets/config.json",
                    "assets/keyinject.exe",
                    "assets/meltapp.exe"    ]
    executed = False
    result = "ERROR GENERAL"

    if _wait_for_startup(vm) is False:
        result = "ERROR wait for startup for %s" % vm_name 
    else:
        copy_to_guest(vm, test_dir, filestocopy)
        job_log(vm_name, "ENVIRONMENT")
        
        # executing bat synchronized
        executed = vmman.executeCmd(vm, "%s\\%s" % (test_dir, buildbat))
        job_log(vm_name, "EXECUTED %s" % kind)

        if executed is False:
            print "DBG %s" % executed 
            print "[%s] Execution failed!" % vm

        print "processes: %s" % vmman.listProcesses(vm)

        #timestamp = time.strftime("%Y%m%d_%H%M", time.gmtime())
        out_img = "%s/screenshot_%s_%s.png" % (logdir, vm, kind)
        vmman.takeScreenshot(vm, out_img)
        
        # save results.txt locally
        result = save_results(vm, kind)
        job_log(vm_name, "FINISHED %s" % kind)
    
    # suspend & refresh snapshot
    if executed:
        vmman.shutdown(vm)
        job_log(vm_name, "SHUTDOWN %s" % kind)
    else:
        vmman.suspend(vm)
        job_log(vm_name, "SUSPENDED %s" % kind)
    return result

def test_internet(vm_name):
    try:
        vm = VMachine(vm_conf_file, vm_name)
        test_dir = "C:\\Users\\avtest\\Desktop\\AVTEST"
        filestocopy =[  "./test_internet.bat",
                        "lib/vmavtest.py",
                        "lib/logger.py",
                        "lib/rcs_client.py" ]
        copy_to_guest(vm, test_dir, filestocopy)
        # executing bat synchronized
        vmman.executeCmd(vm, "%s\\test_internet.bat" % test_dir)
        sleep(random.randint(100,200))
        vmman.shutdown(vm)
        return "[%s] dispatched test internet" % vm_name
    except FailedExecutionException as e:
        raise FailedExecutionException("Error is ", e )
        
def test_exe(args):
    vm_name, exe_path = args
    vm = VMachine(vm_conf_file, vm_name)

    vmman.revertLastSnapshot(vm)
    sleep(5)
    vmman.startup(vm)
    sleep(5 * 60)

    if _wait_for_startup(vm) is False:   
        return "Error wait for startup for %s" % vm_name
    
    test_dir = "C:\\Users\\avtest\\Desktop\\AVTEST"

    filestocopy =[  exe_path ]
    copy_to_guest(vm, test_dir, filestocopy)
    
    # executing bat synchronized
    vmman.executeCmd(vm, "%s\\%s" % (test_dir,exe_dir))

    sleep(random.randint(100,200))

    out_img = "%s/screenshot_%s_%s.png" % (logdir, vm, kind)
    vmman.takeScreenshot(vm, out_img)
    
    # save results.txt locally
    result = save_results(vm)

    vmman.shutdown(vm)

    return result
        
def test(args):
    results=[]
    results.append('silent, avast) 2013-02-27 17:46:53,983: INFO: + FAILED SERVER ERROR\r\n')
    results.append('silent, avira) 2013-02-27 17:46:37,427: INFO: + FAILED SERVER ERROR\r\n')
    results.append('silent, kis) 2013-02-27 17:50:21,430: INFO: + FAILED SERVER ERROR\r\n')
    results.append('silent, norton) Error save')
    report("report.test.txt", results)


def _wait_for_startup(vm, max_count=20):
    count = 0
    while not "vmtoolsd.exe" in vmman.listProcesses(vm):
        sleep(60)
        count+=1
        if count > max_count:
            return False
    return True

def timestamp():
    return time.strftime("%Y%m%d_%H%M", time.gmtime())

def report(filename, results):
    print "[*] RESULTS: " 

    # ordered = {}
    with open( filename, "wb") as f:
        f.write("REPORT\n")
        for l in results:
            #for k,v in l.items():
            print "%s" % l
            if type(l) is list:
                for e in l:
                    f.write(" %s\n" % e)
            else:
                f.write("%s\n" % l)

        # for l in results:
        #     ordered[l]={}
        #     for k,v in l.items():
        #         print "  %s -> %s" % (k,v)
        #         f.write("  %s -> %s" % (k,v))
        #         left, res = v.split("+")
        #         av = left.split()[0]
        #         if res not in ordered.keys():
        #             ordered[res] = []
        #         ordered[res].add(av)
        # f.write("\nSUMMARY\n")
        # keys = ordered.keys()
        # keys.sort()
        # keys.reverse()
        # for k in keys:
        #     f.write("%s:"%k)
        #     for a in ordered[k]:
        #         f.write("  %s" % a)

def main():
    global logdir

    # PARSING

    parser = argparse.ArgumentParser(description='AVMonitor master.')

    parser.add_argument('action', choices=['update', 'revert', 'dispatch', 
        'test', 'command', 'test_internet'],
        help="The operation to perform")
    parser.add_argument('-m', '--vm', required=False, 
        help="Virtual Machine where execute the operation")
    parser.add_argument('-p', '--pool', default=4, type=int, 
        help="This is the number of parallel process (default 2)")
    parser.add_argument('-l', '--logdir', default="/var/log/avmonitor/report",  
        help="Log folder")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,  
        help="Verbose")
    parser.add_argument('-k', '--kind', default="all", type=str,
        help="Verbose")
    parser.add_argument('-c', '--cmd', required=False,
        help="Run VMRUN command")
    args = parser.parse_args()

    # LOGGER

    logdir = "%s/%s_%s" % (args.logdir, args.action, timestamp())
    if not os.path.exists(logdir):
        print "DBG mkdir %s" % logdir
        os.mkdir(logdir)
    sym = "%s/%s" % (args.logdir, args.action)
    if os.path.exists(sym):
        os.unlink(sym)
    os.symlink(logdir, sym)
    lib.logger.setLogger(debug = args.verbose, filelog = "%s/master.logger.txt" % (logdir.rstrip('/')) )

    # GET CONFIGURATION FOR AV UPDATE PROCESS (exe, vms, etc)

    op_conf_file = os.path.join("conf", "vms.cfg")
    
    if args.vm:
        vm_names = args.vm.split(',')
    else:
        # get vm names
        c = ConfigParser()
        c.read(op_conf_file)
        vm_names = c.get("pool", "machines").split(",")

    [ job_log(v, "INIT") for v in vm_names ]

    # TEST

    if args.action == "test":
        #get_results("eset")
        test(args)
        exit(0)

    # SHUT DOWN NETWORK

    if args.action == "update":
        os.system('sudo ./net_enable.sh')
        print "[!] Enabling NETWORKING!"
    else:
        os.system('sudo ./net_disable.sh')
        print "[!] Disabling NETWORKING!"

    # POOL EXECUTION    

    pool = Pool(args.pool)
    print "[*] selected operation %s" % args.action

    actions = { "update" : update, "revert": revert, 
                "dispatch": dispatch, "test_internet": test_internet,
                "command": run_command }

    arg = args.kind
    if args.action == "command":
        arg = args.cmd
    print "MASTER %s on %s" % (arg, vm_names)
    r = pool.map_async(actions[args.action], [ ( n, arg ) for n in vm_names ])
    results = r.get()

    # REPORT
    filename = "%s/master_%s.txt" % (logdir, args.action)
    report(filename, results)



if __name__ == "__main__":	
    main()
