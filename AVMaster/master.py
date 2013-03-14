import argparse
import os
import time
from time import sleep
from ConfigParser import ConfigParser
from multiprocessing import Pool
import random
import os.path
import traceback

from lib.VMachine import VMachine
from lib.VMManager import VMManagerVS
from lib.SphereManager import vSphereManager
from lib.report import Report
#from lib.logger import logger
import lib.logger

vm_conf_file = os.path.join("conf", "vms.cfg")

# get configuration for AV update process (exe, vms, etc)

logdir = ""
vmman = VMManagerVS(vm_conf_file)
updatetime = 50
server = ""

def job_log(vm_name, status):
    print "+ %s: %s" % (vm_name, status)

def update(args):
    try:
        vm_name = args[0]
        vm = VMachine(vm_conf_file, vm_name)
        job_log(vm_name, "UPDATE")

        vmman.revertLastSnapshot(vm)
        job_log(vm_name, "REVERTED")

        sleep(random.randint(60,60*10))
        vmman.startup(vm)
        job_log(vm_name, "STARTED")

        sleep(5 * 60)

        if wait_for_startup(vm) is False:
            job_log(vm_name, "NOT STARTED")
            return "ERROR wait for startup for %s" % vm_name
 
        if check_infection_status(vm) is True:
            vmman.shutdown(vm)
            return "ERROR VM IS INFECTED!!!"
 
        out_img = "%s/screenshot_%s_update.png" % (logdir, vm_name)
        vmman.takeScreenshot(vm, out_img)
        
        print "[%s] waiting for Updates" % vm_name
        sleep(updatetime * 60)
        sleep(random.randint(10,300))

        running = True
        job_log(vm_name, "SHUTDOWN")
        r = vmman.shutdownUpgrade(vm)

        if r is False:
            return "%s, NOT Updated!"  % vm_name

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
            return "%s, SUCCESS: Updated!"  % vm_name
        else:
            job_log(vm_name, "NOT UPDATED")
            return "%s, ERROR: NOT Updated!"  % vm_name

    except Exception as e:
        job_log(vm_name, "ERROR")
        print "DBG trace %s" % traceback.format_exc()
        return "%s, ERROR: not updated. Reason: %s" % (vm_name, e)

def revert(args):
    vm_name = args[0]
    job_log(vm_name, "REVERT")
    vm = VMachine(vm_conf_file, vm_name)
    vmman.revertLastSnapshot(vm)
    sleep(2)
    return "[*] %s reverted!" % vm_name

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

        # avast) 2013-03-05 05:03:09,892: INFO: + FAILED ELITE INSTALL\r\n'
        return "%s, %s, %s" % (vm, kind, last)
    except Exception as e:
        return "%s, %s, ERROR saving results with exception: %s" % (vm, kind, e)

def dispatch(args):
    try:
        vm_name, kind = args
        results = []
        print "DBG %s, %s" %(vm_name,kind)
        if kind == "all":
            results.append( dispatch_kind(vm_name, "silent") )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "melt") )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "exploit") )
        else:
            results.append( dispatch_kind(vm_name, kind) )

        return results
    except Exception as e:
        print "ERROR %s %s" % (kind, e)
        print "DBG trace %s" % traceback.format_exc()
        return {'ERROR': e}

def dispatch_kind(vm_name, kind):
    
    vm = VMachine(vm_conf_file, vm_name)
    job_log(vm_name, "DISPATCH %s" % kind)
    
    vmman.revertLastSnapshot(vm)
    job_log(vm_name, "REVERTED")

    sleep(random.randint(30, 5 * 60))
    vmman.startup(vm)
    sleep(5 * 60)
    job_log(vm_name, "STARTUP")
    
    test_dir = "C:\\Users\\avtest\\Desktop\\AVTEST"

    buildbat = "build_%s_%s.bat" % (kind, server)

    filestocopy =[  "./%s" % buildbat,
                    "lib/vmavtest.py",
                    "lib/logger.py",
                    "lib/rcs_client.py",
                    "conf/vmavtest.cfg",
                    "assets/config_desktop.json",
                    "assets/config_mobile.json",
                    "assets/keyinject.exe",
                    "assets/meltapp.exe",
                    "assets/meltexploit.txt"    ]
    executed = False
    result = "%s, %s, ERROR GENERAL" % (vm_name, kind) 

    if wait_for_startup(vm) is False:
        result = "%s, %s, ERROR: wait for startup for" % (vm_name, kind) 
    else:
        copy_to_guest(vm, test_dir, filestocopy)
        job_log(vm_name, "ENVIRONMENT")
        
        # executing bat synchronized
        executed = vmman.executeCmd(vm, "%s\\%s" % (test_dir, buildbat), interactive=True)
        job_log(vm_name, "EXECUTED %s" % kind)

        if executed is False:
            print "DBG %s" % executed 
            print "%s, ERROR: Execution failed!" % vm

        #print "processes: %s" % vmman.listProcesses(vm)

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

def push(args):
    vm_name, kind = args
    
    vm = VMachine(vm_conf_file, vm_name)
    #job_log(vm_name, "DISPATCH %s" % kind)
    
    #vmman.revertLastSnapshot(vm)
    #job_log(vm_name, "REVERTED")

    #sleep(5)
    #vmman.startup(vm)
    #sleep(5* 60)
    #job_log(vm_name, "STARTUP")
    
    test_dir = "C:\\Users\\avtest\\Desktop\\AVTEST"

    buildbat = "push_%s_%s.bat" % (kind, args.server)

    filestocopy =[  "./%s" % buildbat,
                    "./push_all_minotauro.bat",
                    "lib/vmavtest.py",
                    "lib/logger.py",
                    "lib/rcs_client.py",
                    "conf/vmavtest.cfg",
                    "assets/config_desktop.json",
                    "assets/config_mobile.json",
                    "assets/keyinject.exe",
                    "assets/meltapp.exe",
                    "assets/meltexploit.txt"    ]
    executed = False
    result = "ERROR GENERAL"

    if wait_for_startup(vm) is False:
        result = "ERROR wait for startup for %s" % vm_name 
    else:
        copy_to_guest(vm, test_dir, filestocopy)
        job_log(vm_name, "ENVIRONMENT")
        result = "pushed"
    return result

def test_internet(args):
    vm_name = args[0]
    try:
        vm = VMachine(vm_conf_file, vm_name)
        vmman.startup(vm)
        test_dir = "C:\\Users\\avtest\\Desktop\\TEST_INTERNET"
        filestocopy =[  "./test_internet.bat",
                        "lib/vmavtest.py",
                        "lib/logger.py",
                        "lib/rcs_client.py" ]
        if wait_for_startup(vm) is False:
            result = "ERROR wait for startup for %s" % vm_name 
        else:
            copy_to_guest(vm, test_dir, filestocopy)
            # executing bat synchronized
            vmman.executeCmd(vm, "%s\\test_internet.bat" % test_dir)
            sleep(random.randint(100,200))
            #vmman.shutdown(vm)
            return "[%s] dispatched test internet" % vm_name
    except Exception as e:
        return "[%s] failed test internet. reason: %s" % (vm_name, e)

def check_infection_status(vm):
    startup_dir = "C:\\Users\\avtest\\AppData\\Microsoft"
    stuff = vmman.listDirectoryInGuest(vm, startup_dir)
    print stuff
    if stuff is None:
        return True
    return False
    #if vmman.listDirectoryInGuest(vm) is None:
       
def test(args):
    '''
    results = [
    ['mcafee, silent, 2013-03-13 10:35:01, INFO: + FAILED SCOUT SYNC\r\n', 'mcafee, melt, 2013-03-13 10:55:48, INFO: + FAILED SCOUT SYNC\r\n', 'mcafee, exploit, 2013-03-13 11:15:42, INFO: + FAILED SCOUT SYNC\r\n'],
    ['panda, silent, 2013-03-13 10:33:58, INFO: + FAILED SCOUT SYNC\r\n', 'panda, melt, 2013-03-13 11:19:53, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'panda, exploit, 2013-03-13 11:39:41, INFO: + FAILED SCOUT SYNC\r\n'],
    ['msessential, silent, 2013-03-13 11:00:22, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'msessential, melt, 2013-03-13 11:46:53, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'msessential, exploit, 2013-03-13 12:09:36, INFO: + SUCCESS SCOUT SYNC\r\n'],
    ['avira, silent, 2013-03-13 10:23:12, INFO: + FAILED SCOUT EXECUTE\r\n', 'avira, melt, 2013-03-13 10:43:13, INFO: + FAILED SCOUT SYNC\r\n', 'avira, exploit, 2013-03-13 11:03:46, INFO: + FAILED SCOUT SYNC\r\n'],
    ['pctools, silent, 2013-03-13 11:00:04, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'pctools, melt, 2013-03-13 11:22:04, INFO: + FAILED SCOUT SYNC\r\n', 'pctools, exploit, 2013-03-13 11:42:11, INFO: + FAILED SCOUT SYNC\r\n'],
    ["comodo, silent, ERROR saving results with exception: [Errno 2] No such file or directory: '/var/log/avmonitor/report/dispatch_20130313_0914/results_comodo_silent.txt'", "comodo, melt, ERROR saving results with exception: [Errno 2] No such file or directory: '/var/log/avmonitor/report/dispatch_20130313_0914/results_comodo_melt.txt'", "comodo, exploit, ERROR saving results with exception: [Errno 2] No such file or directory: '/var/log/avmonitor/report/dispatch_20130313_0914/results_comodo_exploit.txt'"]
    ]

    r = Report(results)
    r.send_report_color_mail('dispatch_20130313_0914')
    '''
    conf = ConfigParser()
    conf.read(vm_conf_file)
    vsphere = vSphereManager( conf.get("vsphere", "host"),
                              conf.get("vsphere", "user"),
                              conf.get("vsphere", "passwd") )

    vsphere.connect()
    vm_path = conf.get("vms","zenovm")

    vm = vsphere.get_vm(vm_path)

    print "powering on"
    #vsphere.power_on(vm)

    print "logging in"
    vsphere.login_in_guest(vm, "avtest", "avtest")

    #vm.login_in_guest("avtest","avtest")
    print "ok. logged in"
    vsphere.make_directory(vm, "C:\\Users\\avtest\\Desktop\\tettest")
    print "powering off"
    '''
    vsphere.power_off(vm)
    sleep(60)
    vsphere.create_snapshot(vm, "nuu")
    vpshere.delete_snapshot(vm, "pysphere_test")
    '''





    
def wait_for_startup(vm, max_minute=20):
    count = 0
    while not "vmtoolsd.exe" in vmman.listProcesses(vm):
        sleep(20)
        count+=1
        if count > max_minute*3:
            return False
    return True

def timestamp():
    return time.strftime("%Y%m%d_%H%M", time.gmtime())

def main():
    global logdir

    # PARSING

    parser = argparse.ArgumentParser(description='AVMonitor master.')

    parser.add_argument('action', choices=['update', 'revert', 'dispatch', 
        'test', 'command', 'test_internet', 'push'],
        help="The operation to perform")
    parser.add_argument('-m', '--vm', required=False, 
        help="Virtual Machine where execute the operation")
    parser.add_argument('-p', '--pool', type=int, required=False,
        help="This is the number of parallel process (default 2)")
    parser.add_argument('-l', '--logdir', default="/var/log/avmonitor/report",  
        help="Log folder")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,  
        help="Verbose")
    parser.add_argument('-k', '--kind', default="all", type=str,
        help="Verbose", choices=['silent', 'melt', 'exploit', 'all'])
    parser.add_argument('-c', '--cmd', required=False,
        help="Run VMRUN command")
    parser.add_argument('-u', '--updatetime', default=50, type=int,
        help="Update time in minutes")
    parser.add_argument('-s', '--server', default='minotauro', choices=['minotauro', 'zeus', 'castore', 'polluce'],
        help="Update time in minutes")
    args = parser.parse_args()

    # LOGGER
    print "updatetime: ", args.updatetime
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

    c = ConfigParser()
    c.read(vm_conf_file)

    if args.vm:
        if args.vm == "all":
            vm_names = c.get("pool", "all").split(",")
        else:
            vm_names = args.vm.split(',')
    else:
        # get vm names
        vm_names = c.get("pool", "machines").split(",")

    global server
    server = args.server
    print "DBG server: %s" % server

    [ job_log(v, "INIT") for v in vm_names ]

    global updatetime
    updatetime = args.updatetime

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

    if args.pool:
        pool_size = args.pool
    else:
        pool_size = int(c.get("pool", "size"))

    pool = Pool(pool_size)
    
    print "[*] selected operation %s" % args.action

    actions = { "update" : update, "revert": revert, 
                "dispatch": dispatch, "test_internet": test_internet,
                "command": run_command, "push": push }

    arg = args.kind
    if args.action == "command":
        arg = args.cmd
    print "MASTER %s on %s, action %s, pool %s" % (arg, vm_names, args.action, args.pool)
    r = pool.map_async(actions[args.action], [ ( n, arg ) for n in vm_names ])
    results = r.get()

    # REPORT
    
    rep = Report(results)
    rep.save_file("%s/master_%s.txt" % (logdir, args.action))

    
    if args.action == "dispatch":
        html_file = "%s/report_%s.html" % (logdir, args.action)
        if rep.save_html(html_file) is False:
            print "[!] Problem creating HTML Report!"
        if rep.send_report_color_mail(html_file, logdir.split('/')[-1]) is False:
            print "[!] Problem sending HTML email Report!"
    else:
        if rep.send_mail() is False:
            print "[!] Problem sending mail!"

    os.system('sudo ./net_disable.sh')    
    print "[!] Disabling NETWORKING!"

if __name__ == "__main__":	
    main()
