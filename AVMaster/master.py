import argparse
import os
import time
import random
import os.path
import traceback
import sqlite3

from time import sleep
from ConfigParser import ConfigParser
from multiprocessing import Pool
from redis import Redis
from flask.ext.sqlalchemy import SQLAlchemy

from lib.core.VMachine import VMachine
from lib.core.VMManager import vSphere, VMRun
from lib.core.report import Report
from lib.web.models import db, app, init_db, Test, Result
from lib.web.settings import DB_PATH
from lib.core.logger import setLogger

vm_conf_file = os.path.join("conf", "vms.cfg")

# get configuration for AV update process (exe, vms, etc)

logdir = ""
test_id = -1
status = 0

vmman = VMRun(vm_conf_file)

#vsphere = vSphere( vm_conf_file )
#vsphere.connect()

updatetime = 50

def job_log(vm_name, status):
    print "+ %s: %s" % (vm_name, status)

def update(flargs):
    vms = len(args.vm.split(","))
    try:
        vm_name = args[0]
        vm = VMachine(vm_config_file, vm_name)
        job_log(vm_name, "UPDATE")

        vm.revert_last_snapshot()
        job_log(vm_name, "REVERTED")

        sleep(random.randint(60, 60 * vms))
        vm.startup()
        job_log(vm_name, "STARTED")

        sleep(5 * 60)

        if wait_for_startup(vm) is False:
            job_log(vm_name, "NOT STARTED")
            return "ERROR wait for startup for %s" % vm_name
 
        if check_infection_status(vm) is True:
            vm.shutdown()
            return "ERROR VM IS INFECTED!!!"
 
        out_img = "%s/screenshot_%s_update.png" % (logdir, vm_name)
        vmman.takeScreenshot(vm, out_img)
        
        print "[%s] waiting for Updates" % vm_name
        sleep(updatetime * 60)
        sleep(random.randint(10,300))

        running = True
        job_log(vm_name, "SHUTDOWN")
        r = vm.shutdown_upgrade()

        if r is False:
            return "%s, NOT Updated!"  % vm_name

        count = 0
        sh = True

        if sh == True:
            vm.refresh_snapshot()
            job_log(vm_name, "UPDATED")
            return "%s, SUCCESS: Updated!"  % vm_name
        else:
            job_log(vm_name, "NOT UPDATED")
            return "%s, ERROR: NOT Updated!"  % vm_name

    except Exception as e:
        job_log(vm_name, "ERROR")
        print "DBG trace %s" % traceback.format_exc()
        return "%s, ERROR: not updated. Reason: %s" % (vm_name, e)

def revert(flargs):
    vm_name = flargs[0]
    job_log(vm_name, "REVERT")
    vm = VMachine(vm_conf_file, vm_name)
    vm.revert_last_snapshot()
    return "[*] %s reverted!" % vm_name

def run_command(flargs):
        #arg = args.kind
    #if args.action == "command":
    #    arg = args.cmd
    vm_name, args = flargs
    cmd = args.cmd
    if cmd is None:
        return False
    vm = VMachine(vm_conf_file, vm_name)
    vm._run_cmd(cmd)

    return True

def start_test():
    try:
        timestamp = time.strftime("%Y%m%d_%H%M", time.gmtime())
        
        t = Test(0,str(timestamp))
        db.session.add(t)
        db.session.commit()
        return t.id
    except Exception as e:
        print "DBG error inserting report in db. Exception: %s" % e
        print DB_PATH
        return None

def add_record_result(vm_name, kind, t_id, status, results=None):
    try:
        timestamp = time.strftime("%Y%m%d_%H%M", time.gmtime())

        r = Result(t_id, vm_name, kind, status, res_full=results)
        db.session.add(r)
        db.session.commit()
    except Exception as e:
        print "DBG error inserting results of test in db. Exception: %s" % e

def save_results(vm, kind):
    try:
        res_file_rem = "c:\\Users\\avtest\\Desktop\\AVTEST\\results.txt"
        res_file_loc = "%s/results_%s_%s.txt" % (logdir, vm, kind)
        print "DBG saving %s %s"
        vm.get_file(res_file_rem, res_file_loc)

        last = "ERROR save"
        f = open(res_file_loc, 'rb')
        for l in f.readlines():
            if " + " in l:
                last = l

        # avast) 2013-03-05 05:03:09,892: INFO: + FAILED ELITE INSTALL\r\n'
        return "%s, %s, %s" % (vm, kind, last)
    except Exception as e:
        return "%s, %s, ERROR saving results with exception: %s" % (vm, kind, e)

def dispatch(flargs):
    global status, test_id

    try:
        vm_name, args = flargs
        kind = args.kind
        results = []
        print "DBG %s, %s" %(vm_name,kind)

        # add record to db
        print "DBG add record to db"
        test_id = start_test()

        if test_id == -1:
            print "DBG test_id not found"

        if kind == "all":
            results.append( dispatch_kind(vm_name, "silent", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "melt", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "exploit", args) )
        else:
            results.append( dispatch_kind(vm_name, kind, args) )

        return results
    except Exception as e:
        print "ERROR %s %s" % (kind, e)
        print "DBG trace %s" % traceback.format_exc()
        return {'ERROR': e}

def dispatch_kind(vm_name, kind, args):
    global status

    vms = len(args.vms)
    
    vm = VMachine(vm_conf_file, vm_name)
    job_log(vm_name, "DISPATCH %s" % kind)
    
    vm.revert_last_snapshot()
    job_log(vm_name, "REVERTED")

    sleep(random.randint(30, vms * 30))
    vm.startup()
    job_log(vm_name, "STARTUP")

    status+=1

    test_dir = "C:\\Users\\avtest\\Desktop\\AVTEST"

    buildbat = "build_%s_%s.bat" % (kind, args.server)

    filestocopy =[  "./%s" % buildbat,
                    "lib/agent.py",
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
        #vm.login_in_guest()
        job_log(vm_name, "LOGGED")
        vm.send_files("../AVAgent", test_dir, filestocopy)
        job_log(vm_name, "ENVIRONMENT")
        
        # executing bat synchronized
        executed = vmman.executeCmd(vm, "%s\\%s" % (test_dir, buildbat), interactive=True)
        #vsphere.execute_cmd(vm, "%s\\%s" % (test_dir, buildbat))
        job_log(vm_name, "EXECUTED %s" % kind)

        if executed is False:
            print "DBG %s" % executed 
            print "%s, ERROR: Execution failed!" % vm
        
        #print "processes: %s" % vmman.listProcesses(vm)

        #timestamp = time.strftime("%Y%m%d_%H%M", time.gmtime())
        out_img = "%s/screenshot_%s_%s.png" % (logdir, vm, kind)
        vmman.takeScreenshot(vm, out_img)
        job_log(vm_name, "SCREENSHOT ok")

        # save results.txt locally
        result = save_results(vm, kind)
        job_log(vm_name, "SAVED %s" % kind)
    
    # suspend & refresh snapshot
    if executed:
        vm.shutdown()
        job_log(vm_name, "SHUTDOWN %s" % kind)
    else:
        vm.suspend()
        job_log(vm_name, "SUSPENDED %s" % kind)

    if test_id != -1:
        status+=1
        print "DBG test_id: %s, status: %s" % (test_id, status)
        add_record_result(vm_name, kind, test_id, status, result)
    else:
        print "DBG no test_id found for %s, %s" % (vm_name, kind)

    return result

def push(flargs):
    vm_name, args = flargs
    kind = args.kind
    
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
                    "lib/agent.py",
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

def test_internet(flargs):
    vm_name = flargs[0]
    try:
        vm = VMachine(vm_conf_file, vm_name)
        vm.startup()
        test_dir = "C:\\Users\\avtest\\Desktop\\TEST_INTERNET"
        filestocopy =[  "./test_internet.bat",
                        "lib/agent.py",
                        "lib/logger.py",
                        "lib/rcs_client.py" ]
        if wait_for_startup(vm) is False:
            result = "ERROR wait for startup for %s" % vm_name 
        else:
            copy_to_guest(vm, test_dir, filestocopy)
            # executing bat synchronized
            vm.execute_cmd("%s\\test_internet.bat" % test_dir)
            sleep(random.randint(100,200))
            #vmman.shutdown(vm)
            return "[%s] dispatched test internet" % vm_name
    except Exception as e:
        return "[%s] failed test internet. reason: %s" % (vm_name, e)

def check_infection_status(vm):
    startup_dir = "C:\\Users\\avtest\\AppData\\Microsoft"
    stuff = vm.list_directory(startup_dir)
    print stuff
    if stuff is None:
        return True
    return False
       
def test(flargs):
    conf = ConfigParser()
    conf.read(vm_conf_file)

    res = "FAILED"
    t_id = add_record_test(1,"21/09/2123 20:44")
    add_record_result(t_id, "noav", "melt", 3, res)
    
def wait_for_startup(vm, max_minute=20):
    global status

    r = Redis()

    p = r.pubsub()
    p.subscribe(vm.name)

    # timeout
    for m in p.listen():
        print "DBG %s"  % m
        try:
            if "STARTED" in m['data']:
                status+=1
                return True
        except TypeError:
            pass

def timestamp():
    return time.strftime("%Y%m%d_%H%M", time.gmtime())

def main():
    global logdir, status, test_id

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
        help="Kind of test", choices=['silent', 'melt', 'exploit', 'all'])
    parser.add_argument('-c', '--cmd', required=False,
        help="Run VMRUN command")
    parser.add_argument('-u', '--updatetime', default=50, type=int,
        help="Update time in minutes")
    parser.add_argument('-s', '--server', default='minotauro', choices=['minotauro', 'zeus', 'castore', 'polluce'],
        help="Server name")
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
    setLogger(debug = args.verbose, filelog = "%s/master.logger.txt" % (logdir.rstrip('/')) )

    # GET CONFIGURATION FOR AV UPDATE PROCESS (exe, vms, etc)

    c = ConfigParser()
    c.read(vm_conf_file)

    vSphere.hostname = c.get("vsphere", "host")
    vSphere.username = c.get("vsphere", "user")
    vSphere.password = c.get("vsphere", "passwd")

    if args.vm:
        if args.vm == "all":
            vm_names = c.get("pool", "all").split(",")
        else:
            vm_names = args.vm.split(',')
    else:
        # get vm names
        vm_names = c.get("pool", "machines").split(",")
    args.vms = vm_names
    #global server
    #server = args.server
    #print "DBG server: %s" % server

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
        args.pool = pool_size

    pool = Pool(pool_size)
    
    print "[*] selected operation %s" % args.action

    actions = { "update" : update, "revert": revert, 
                "dispatch": dispatch, "test_internet": test_internet,
                "command": run_command, "push": push }

    #arg = args.kind
    #if args.action == "command":
    #    arg = args.cmd
    #print "MASTER %s on %s, action %s, pool %s" % (arg, vm_names, args.action, args.pool)
    print "MASTER on %s, action %s" % (vm_names, args.action)
    r = pool.map_async(actions[args.action], [ ( n, args ) for n in vm_names ])
    results = r.get()

    # REPORT
    
    rep = Report(results)
    rep.save_file("%s/master_%s.txt" % (logdir, args.action))

    
    if args.action == "dispatch":
        html_file = "%s/report_%s.html" % (logdir, args.action)
        if rep.save_html(html_file) is False:
            print "[!] Problem creating HTML Report!"
        if rep.save_db(test_id) is False:
            print "[!] Problem saving results on db!"
        if rep.send_report_color_mail(logdir.split('/')[-1]) is False:
            print "[!] Problem sending HTML email Report!"
    else:
        if rep.send_mail() is False:
            print "[!] Problem sending mail!"

    os.system('sudo ./net_disable.sh')    
    print "[!] Disabling NETWORKING!"

if __name__ == "__main__":	
    main()
