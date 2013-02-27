import argparse
import os
import time
from time import sleep
from ConfigParser import ConfigParser
from multiprocessing import Pool
import argparse
import random
import os.path
import signal

from lib.VMachine import VMachine
from lib.VMManager import VMManagerVS
#from lib.logger import logger
import lib.logger

vm_conf_file = os.path.join("conf", "vms.cfg")
op_conf_file = os.path.join("conf", "operations.cfg")

# get configuration for AV update process (exe, vms, etc)

logdir = ""
vmman = VMManagerVS(vm_conf_file)

jobs = {}
def job_log(vm_name, status):
    print "+ %s: %s" % (vm_name, status)

    if False:
        if not vm_name in jobs.keys():
            jobs[vm_name] = (0, "VOID")
        
        (count, _) = jobs[vm_name]

        jobs[vm_name] = (count + 1, status)

        print "JOB %s" % [ (k,vc) for k, (vc,vs) in  jobs.items() ]

def receive_signal(signum, stack):
    print 'JOBS:', jobs

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

        if wait_for_startup(vm) is False:
            job_log(vm_name, "NOT STARTED")
            return "Error wait for startup for %s" % vm_name

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
    #vmman._run_cmd(vmx, cmd, args)
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

def save_results(vm):
    try:
        timestamp = time.strftime("%Y%m%d_%H%M", time.gmtime())
        filename = "%s/results_%s_%s.txt" % (logdir, vm, timestamp)
        vmman.copyFileFromGuest(vm, "c:\\Users\\avtest\\Desktop\\AVTEST\\results.txt", filename)

        last = "Error save"
        f = open(filename, 'rb')
        for l in f.readlines():
            if " + " in l:
                last = l

        return "%s %s" % (vm, last)
    except Exception as e:
        return "[%s] Error saving results with exception: %s" % (vm,e)

def dispatch(args):    
    vm_name, kind = args
    print "DBG %s, %s" %(vm_name,kind)
    if kind == "all":
        dispatch_kind(vm_name, "silent")
        sleep(random.randint(5,10))
        dispatch_kind(vm_name, "melt")
    else:
        dispatch_kind(vm_name, kind)

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

    host = "minotauro"

    buildbat = "build_%s_%s.bat" % (kind, host)

    
    filestocopy =[  "./%s" % buildbat,
                    "lib/vmavtest.py",
                    "lib/logger.py",
                    "lib/rcs_client.py",
                    "conf/vmavtest.cfg",
                    "assets/config.json",
                    "assets/keyinject.exe",
                    "assets/meltapp.exe"    ]

    if wait_for_startup(vm) is False:
        return "Error wait for startup for %s" % vm_name

    copy_to_guest(vm, test_dir, filestocopy)
    job_log(vm_name, "ENVIRONMENT")
    
    # executing bat synchronized
    r = vmman.executeCmd(vm, "%s\\%s" % (test_dir, buildbat))
    job_log(vm_name, "EXECUTED %s" % kind)

    if r is False:
        print "DBG %s" % r 
        print "[%s] Execution failed!" % vm

    #timestamp = time.strftime("%Y%m%d_%H%M", time.gmtime())
    out_img = "%s/screenshot_%s_%s.png" % (logdir, vm, kind)
    vmman.takeScreenshot(vm, out_img)
    
    # save results.txt locally
    result = save_results(vm)

    # suspend & refresh snapshot
    if r == True:
        vmman.shutdown(vm)
    #sleep(5)
    #vmman.refreshSnapshot(vm, vm.snapshot)
    job_log(vm_name, "FINISHED %s" % kind)
    return result


def test_internet(vm_name):
    try:
        vm = VMachine(vm_conf_file, vm_name)

        #vmman.revertLastSnapshot(vm)
        #sleep(5)
        #vmman.startup(vm)
        #sleep(5 * 60)
        
        test_dir = "C:\\Users\\avtest\\Desktop\\AVTEST"

        filestocopy =[  "./test_internet.bat",
                        "lib/vmavtest.py",
                        "lib/logger.py",
                        "lib/rcs_client.py" ]
        copy_to_guest(vm, test_dir, filestocopy)
        
        # executing bat synchronized
        vmman.executeCmd(vm, "%s\\test_internet.bat" % test_dir)
        return "[%s] dispatched test internet" % vm_name
    except FailedExecutionException as e:
        raise FailedExecutionException("Error is ", e )
        

def test(args):
    run_command(args.vm, args.cmd)

def wait_for_startup(vm, max_count=20):
    count = 0
    while not "vmtoolsd.exe" in vmman.listProcesses(vm):
        sleep(60)
        count+=1
        if count > max_count:
            return False
    return True

def timestamp():
    return time.strftime("%Y%m%d_%H%M", time.gmtime())

def main():
    global logdir
    signal.signal(signal.SIGUSR1, receive_signal)

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

    logdir = "%s/%s_%s" % (args.logdir, args.action, timestamp())
    if not os.path.exists(logdir):
        print "DBG mkdir %s" % logdir
        os.mkdir(logdir)
    lib.logger.setLogger(debug = args.verbose, filelog = "%s/master.logger.txt" % (logdir.rstrip('/')) )

    if args.action == "test":
        #get_results("eset")
        test(args)
        exit(0)

    # shut down network
    if args.action == "update":
        os.system('sudo ./net_enable.sh')
        print "[!] Enabling NETWORKING!"
    else:
        os.system('sudo ./net_disable.sh')
        print "[!] Disabling NETWORKING!"

    op_conf_file = os.path.join("conf", "vms.cfg")
    # get configuration for AV update process (exe, vms, etc)

    if args.vm:
        vm_names = args.vm.split(',')
    else:
        # get vm names
        c = ConfigParser()
        c.read(op_conf_file)
        vm_names = c.get("pool", "machines").split(",")

    [ job_log(v, "INIT") for v in vm_names ]

    pool = Pool(args.pool)
    print "[*] selected operation %s" % args.action

    actions = { "update" : update, "revert": revert, 
                "dispatch": dispatch, "test_internet": test_internet,
                "command": run_command }

    arg = args.kind
    if args.action == "command":
        arg = args.cmd
    print args.action, arg
    r = pool.map_async(actions[args.action], [ ( n, arg ) for n in vm_names ])
    
    results = r.get()

    print "[*] RESULTS: %s" % results
    print jobs

    with open( "%s/master_%s.txt" % (logdir, args.action), "wb") as f:
        f.write("REPORT\n")
        for l in results:
            f.write("%s" % l)


if __name__ == "__main__":	
    main()
