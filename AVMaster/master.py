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

        sleep(random.randint(10,60))
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
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "mobile") )
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

    sleep(5)
    vmman.startup(vm)
    sleep(5* 60)
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
                    "assets/meltexploit.txt",
                    "assets/meltexploit.docx",
                    "assets/meltexploit.ppt"     ]

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
    job_log(vm_name, "STARTUP")
    
    test_dir = "C:\\Users\\avtest\\Desktop\\AVTEST"

    buildbat = "push_%s_%s.bat" % (kind, server)

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
                    "assets/meltexploit.txt",
                    "assets/meltexploit.docx",
                    "assets/meltexploit.ppt"    ]
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
    results = [
    ['avira, silent, 2013-03-14 10:14:33, INFO: + FAILED SCOUT EXECUTE\r\n', 'avira, melt, 2013-03-14 10:39:00, INFO: + FAILED SCOUT SYNC\r\n', 'avira, exploit, 2013-03-14 11:00:29, INFO: + FAILED SCOUT SYNC\r\n'],
    ['eset, silent, 2013-03-14 10:23:26, INFO: + FAILED SCOUT SYNC\r\n', 'eset, melt, 2013-03-14 10:46:24, INFO: + FAILED SCOUT SYNC\r\n', 'eset, exploit, 2013-03-14 11:12:24, INFO: + FAILED SCOUT SYNC\r\n'],
    ['fsecure, silent, 2013-03-14 10:48:17, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'fsecure, melt, 2013-03-14 11:38:56, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'fsecure, exploit, 2013-03-14 12:00:25, INFO: + SUCCESS SCOUT SYNC\r\n'],
    ['gdata, silent, 2013-03-14 10:19:02, INFO: + SUCCESS ELITE BLACKLISTED\r\n', 'gdata, melt, 2013-03-14 10:37:03, INFO: + SUCCESS ELITE BLACKLISTED\r\n', 'gdata, exploit, 2013-03-14 11:09:17, INFO: + SUCCESS SCOUT SYNC\r\n'],
    ['mcafee, silent, 2013-03-14 10:21:29, INFO: + FAILED SCOUT SYNC\r\n', 'mcafee, melt, 2013-03-14 10:45:21, INFO: + FAILED SCOUT SYNC\r\n', 'mcafee, exploit, 2013-03-14 11:10:34, INFO: + FAILED SCOUT SYNC\r\n'],
    ['msessential, silent, 2013-03-14 10:20:26, INFO: + SUCCESS SCOUT SYNC\r\n', 'msessential, melt, 2013-03-14 11:01:02, INFO: + SUCCESS SCOUT SYNC\r\n', 'msessential, exploit, 2013-03-14 11:37:08, INFO: + SUCCESS SCOUT SYNC\r\n'],
    ['norton, silent, 2013-03-14 10:48:07, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'norton, melt, 2013-03-14 11:38:05, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'norton, exploit, 2013-03-14 12:02:31, INFO: + SUCCESS SCOUT SYNC\r\n'],
    ['panda, silent, 2013-03-14 10:22:30, INFO: + FAILED SCOUT SYNC\r\n', 'panda, melt, 2013-03-14 11:13:02, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'panda, exploit, 2013-03-14 11:37:59, INFO: + FAILED SCOUT SYNC\r\n'],
    ['trendm, silent, 2013-03-14 10:48:01, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'trendm, melt, 2013-03-14 11:39:32, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'trendm, exploit, 2013-03-14 12:02:22, INFO: + SUCCESS SCOUT SYNC\r\n'],
    ['pctools, silent, 2013-03-14 10:41:10, INFO: + SUCCESS SCOUT SYNC\r\n', 'pctools, melt, 2013-03-14 11:37:05, INFO: + FAILED SCOUT SYNC\r\n', 'pctools, exploit, 2013-03-14 12:13:21, INFO: + FAILED SCOUT SYNC\r\n'],
    ['avg, silent, 2013-03-14 10:49:13, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'avg, melt, 2013-03-14 11:39:02, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'avg, exploit, 2013-03-14 12:03:23, INFO: + SUCCESS SCOUT SYNC\r\n'],
    ['bitdef, silent, 2013-03-14 11:18:52, INFO: + SUCCESS ELITE BLACKLISTED\r\n', 'bitdef, melt, 2013-03-14 11:38:39, INFO: + SUCCESS ELITE BLACKLISTED\r\n', 'bitdef, exploit, 2013-03-14 12:01:05, INFO: + SUCCESS SCOUT SYNC\r\n'],
    ['sophos, silent, 2013-03-14 11:31:20, INFO: + FAILED SCOUT SYNC\r\n', 'sophos, melt, 2013-03-14 11:55:39, INFO: + FAILED SCOUT SYNC\r\n', 'sophos, exploit, 2013-03-14 12:19:33, INFO: + FAILED SCOUT SYNC\r\n'],
    ['zoneal, silent, 2013-03-14 11:59:42, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'zoneal, melt, 2013-03-14 12:48:00, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'zoneal, exploit, 2013-03-14 13:08:56, INFO: + SUCCESS SCOUT SYNC\r\n'],
    ['ahnlab, silent, 2013-03-14 12:04:05, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'ahnlab, melt, 2013-03-14 12:55:03, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'ahnlab, exploit, 2013-03-14 13:31:21, INFO: + SUCCESS SCOUT SYNC\r\n'],
    ['norman, silent, 2013-03-14 12:33:00, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'norman, melt, 2013-03-14 13:23:48, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'norman, exploit, 2013-03-14 13:42:35, INFO: + SUCCESS SCOUT SYNC\r\n'],
    ["comodo, silent, ERROR saving results with exception: [Errno 2] No such file or directory: '/var/log/avmonitor/report/dispatch_20130314_0900/results_comodo_silent.txt'", "comodo, melt, ERROR saving results with exception: [Errno 2] No such file or directory: '/var/log/avmonitor/report/dispatch_20130314_0900/results_comodo_melt.txt'", "comodo, exploit, ERROR saving results with exception: [Errno 2] No such file or directory: '/var/log/avmonitor/report/dispatch_20130314_0900/results_comodo_exploit.txt'"],
    ['drweb, silent, 2013-03-14 12:22:05, INFO: + FAILED SCOUT SYNC\r\n', 'drweb, melt, 2013-03-14 12:46:31, INFO: + FAILED SCOUT SYNC\r\n', 'drweb, exploit, 2013-03-14 13:10:12, INFO: + FAILED SCOUT SYNC\r\n'],
    ['kis, silent, 2013-03-14 12:51:06, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'kis, melt, 2013-03-14 13:39:55, INFO: + SUCCESS ELITE UNINSTALLED\r\n', 'kis, exploit, 2013-03-14 13:59:47, INFO: + SUCCESS SCOUT SYNC\r\n'],
    ["emsisoft, silent, ERROR saving results with exception: [Errno 2] No such file or directory: '/var/log/avmonitor/report/dispatch_20130314_0900/results_emsisoft_silent.txt'", "emsisoft, melt, ERROR saving results with exception: [Errno 2] No such file or directory: '/var/log/avmonitor/report/dispatch_20130314_0900/results_emsisoft_melt.txt'", "emsisoft, exploit, ERROR saving results with exception: [Errno 2] No such file or directory: '/var/log/avmonitor/report/dispatch_20130314_0900/results_emsisoft_exploit.txt'"],
    ]

    r = Report(results)
    r.send_report_color_mail('dispatch_20130314_0900')


    
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
        help="Verbose", choices=['silent', 'melt', 'exploit', 'exploit_docx', 'exploit_ppt', 'mobile', 'all'])
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
        if rep.send_report_color_mail(logdir.split('/')[-1]) is False:
            print "[!] Problem sending HTML email Report!"
    else:
        if rep.send_mail() is False:
            print "[!] Problem sending mail!"

    
    os.system('sudo ./net_disable.sh')    
    print "[!] Disabling NETWORKING!"


if __name__ == "__main__":	
    main()
