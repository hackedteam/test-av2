import argparse
import os
import time
import random
import os.path
import traceback
import sqlite3

from base64 import b64encode
from time import sleep
from ConfigParser import ConfigParser
from multiprocessing import Pool
from redis import Redis, StrictRedis
from redis.exceptions import ConnectionError
from flask.ext.sqlalchemy import SQLAlchemy

from lib.core.VMachine import VMachine
from lib.core.VMManager import vSphere, VMRun
from lib.core.report import Report
from lib.web.models import db, app, Test, Result
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
    vms = len(flargs[1].vms)
    try:
        vm_name = flargs[0]
        vm = VMachine(vm_conf_file, vm_name)
        job_log(vm_name, "UPDATE")

        vm.revert_last_snapshot()
        job_log(vm_name, "REVERTED")

        sleep(random.randint(60, 60 * vms))
        vm.startup()
        job_log(vm_name, "STARTED")

        #sleep(5 * 60)

        if wait_for_startup(vm) is False:
            job_log(vm_name, "NOT STARTED")
            return "ERROR wait for startup for %s" % vm_name
 
        if check_infection_status(vm) is not True:
            vm.shutdown()
            return "ERROR VM IS INFECTED!!!"
 
        out_img = "%s/screenshot_%s_update.png" % (logdir, vm_name)
        vmman.takeScreenshot(vm, out_img)
        
        print "[%s] waiting for Updates" % vm_name
        sleep(updatetime * 60)
        sleep(random.randint(10,300))

        job_log(vm_name, "SHUTDOWN")
        r = vmman.shutdownUpgrade(vm)

        if r is False:
            job_log(vm_name, "NOT UPDATED")
            return "%s, ERROR: NOT Updated! no shutdown..."  % vm_name
        else:

            # RESTART TIME
            while vm.is_powered_off() is False:
                sleep(60)

            job_log(vm_name, "POWERED OFF")

            vm.startup()

            if wait_for_startup(vm) is False:
                job_log(vm_name, "NOT RESTARTED")

            vm.shutdown()
            job_log(vm_name, "RESTARTED")

            vm.refresh_snapshot()
            job_log(vm_name, "UPDATED")
            return "%s, SUCCESS: Updated!"  % vm_name
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

def end_test(t_id):
    try:
        t = Test.query.filter_by(id=t_id)
        if t is None:
            return False
        t.status = 1
        db.session.add(t)
        db.session.commit()
        return True
    except Exception as e:
        print "DBG error changing test status to completed. Exception: %s" % e
        return False

def add_record_result(vm_name, kind, t_id, status, result=None):
    try:
        timestamp = time.strftime("%Y%m%d_%H%M", time.gmtime())
        r = Result(vm_name, t_id, kind, status, result)
        db.session.add(r)
        db.session.commit()
        return r.id
    except Exception as e:
        print "DBG error inserting results of test in db. Exception: %s" % e
        return

def upd_record_result(r_id, status=None, result=None):
    r = Result.query.filter_by(id=r_id).first()
    if not r:
        print "DBG result not found"
        return
    print "DBG result: %s" % result
    if result is not None:
        r.result = result
        db.session.commit()
    if status is not None:
        r.status = status
        db.session.commit()

def save_results(vm, kind, test_id, result_id):
    global status, logdir
    
    try:
        if kind == "silent" or kind == "melt":
            max_minute = 60
        elif kind == "exploit":
            max_minute = 30
        elif kind == "mobile" or "exploit_" in kind:
            max_minute = 5  
        results = wait_for_results(vm, result_id, max_minute)

        print "DBG [%s] passing debug files txt from host" % vm.name
        res_txt_dst = "%s/results_%s_%s.txt" % (logdir, vm, kind)
        res_txt_src = "C:\\Users\\avtest\\Desktop\\AVTEST\\results.txt"
        vm.get_file(res_txt_src, res_txt_dst)

        print "DBG results are %s" % results
        return "%s, %s, %s" % (vm.name, kind, results[-1])
    except Exception as e:
        return "%s, %s, ERROR saving results with exception: %s" % (vm, kind, e)

def save_screenshot(vm, result_id):
    try:
        #out_img = "/tmp/screenshot_%s_%s.png" % (vm, kind)
        out_img = "/tmp/screenshot_%s.png" % vm
        vmman.takeScreenshot(vm, out_img)
        with open(out_img, 'rb') as f:
            result = Result.query.filter_by(id=result_id).first_or_404()
            #result.scrshoot = b64encode(f.read())
            result.scrshot = f.read()
            db.session.commit()
        return True
    except Exception as e:
        print "DBG image was not saved. Exception handled: %s" % e
        return False

def save_logs(result_id, log):
    try:
        result = Result.query.filter_by(id=result_id).first_or_404()
        result.log = log
        db.session.commit()
    except Exception as e:
        print "DBG failed saving results log. Exception: %s" % e

def copy_to_guest(vm, test_dir, filestocopy):
    #lib_dir = "%s\\lib" % test_dir
    #assets_dir = "%s\\assets" % test_dir
    vmavtest = "../AVAgent"

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

        print "DBG %s copy %s -> %s" % (vm.name, src, dst)
        vmman.copyFileToGuest(vm, src, dst)

def dispatch(flargs):

    try:
        vm_name, args = flargs
        kind = args.kind
        results = []
        print "DBG %s, %s" %(vm_name,kind)

        if kind == "agents":
            results.append( dispatch_kind(vm_name, "silent", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "mobile", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "exploit_docx", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "exploit_web", args) )
        elif kind == "exploits":
            results.append( dispatch_kind(vm_name, "exploit", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "exploit_docx", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "exploit_ppsx", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "exploit_web", args) )
        elif kind == "all":
            results.append( dispatch_kind(vm_name, "silent", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "melt", args) )
            sleep(random.randint(5,10))
#            results.append( dispatch_kind(vm_name, "exploit", args) )
#            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "exploit_docx", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "exploit_web", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "mobile", args) )
        else:
            results.append( dispatch_kind(vm_name, kind, args) )

        return results
    except Exception as e:
        print "ERROR %s %s" % (kind, e)
        print "DBG trace %s" % traceback.format_exc()
        return {'ERROR': e}

def dispatch_kind(vm_name, kind, args):
    global status, test_id

    print "DBG test_id is %s" % test_id

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
                    "assets/meltexploit.txt",
                    "assets/meltexploit.docx",
                    "assets/meltexploit.ppsx"     ]

    if kind == "exploit_web":
        filestocopy.append("assets/avtest.swf")
        filestocopy.append("assets/owned.docm")
        filestocopy.append("assets/PMIEFuck-WinWord.dll")

    result = "%s, %s, ERROR GENERAL" % (vm_name, kind) 

    if wait_for_startup(vm) is False:
        result = "%s, %s, ERROR not STARTED" % (vm_name, kind)
        result_id = add_record_result(vm_name, kind, test_id, status, result)
    else:
        #vm.login_in_guest()
        result_id = add_record_result(vm_name, kind, test_id, status, "STARTED")
        print "DBG added result with id %s" % result_id

        job_log(vm_name, "LOGGED")
#        vm.send_files("../AVAgent", test_dir, filestocopy)
        copy_to_guest(vm, test_dir, filestocopy)
        #for f in filestocopy:
        #    vm.
        job_log(vm_name, "ENVIRONMENT")
        
        # executing bat synchronized
        vmman.executeCmd(vm, "%s\\%s" % (test_dir, buildbat), interactive=True, bg=True)
        job_log(vm_name, "EXECUTED %s" % kind)

        result = save_results(vm, kind, test_id, result_id)
        job_log(vm_name, "SAVED %s" % kind)
    
        #timestamp = time.strftime("%Y%m%d_%H%M", time.gmtime())
        if save_screenshot(vm, result_id) is True:
            job_log(vm_name, "SCREENSHOT ok")

        
    # suspend & refresh snapshot
    #vm.suspend()
    vm.shutdown()
    job_log(vm_name, "SUSPENDED %s" % kind)

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
                    "assets/meltexploit.txt",
                    "assets/meltexploit.docx",
                    "assets/meltexploit.ppsx"    ]

    result = "ERROR GENERAL"

    if wait_for_startup(vm) is False:
        result = "ERROR wait for startup for %s" % vm_name 
    else:
        vm.send_files("../AVAgent", test_dir, filestocopy)
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
            vm.send_files("../AVAgent", test_dir, filestocopy)
            # executing bat synchronized
            vm.execute_cmd("%s\\test_internet.bat" % test_dir)
            sleep(random.randint(100,200))
            #vmman.shutdown(vm)
            return "[%s] dispatched test internet" % vm_name
    except Exception as e:
        return "[%s] failed test internet. reason: %s" % (vm_name, e)

def check_infection_status(vm):
    startup_dir = "C:\\Users\\avtest\\AppData\\Microsoft"
    stuff = check_directory(vm, startup_dir)
    print stuff
    if stuff is None:
        return True
    test_dir = "C:\\Users\\avtest\\Desktop\\AVTEST"
    test = check_directory(vm, test_dir)
    print test
    if test is None:
        return True
    return False

def check_directory(vm, directory):
    return vm.list_directory(directory)

def test(flargs):
    ''' 
    conf = ConfigParser()
    conf.read(vm_conf_file)
    
    #results = [['comodo, silent, SUCCESS ELITE BLACKLISTED'], ['norton, silent, SUCCESS ELITE UNINSTALLED'], ['pctools, silent, SUCCESS ELITE UNINSTALLED']]

    print "DBG TEST START"

    r = Report(results)
    r.save_db(1)

    print "DBG TEST END"
    '''
    results = [['fakeav, silent, STARTED', 
        'fakeav, melt, ERROR', 
        'fakeav, exploit, SUCCESS', 
        'fakeav, exploit_ppsx, FAILED']]

    rep = Report(9999, results)
    if rep.send_report_color_mail("reportz") is False:
        print "[!] Problem sending HTML email Report!"


def wait_for_startup(vm, message=None, max_minute=8):
    #r = Redis()
    r = StrictRedis(socket_timeout=max_minute * 60)

    p = r.pubsub()
    p.subscribe(vm.name)

    # timeout
    try:
        for m in p.listen():
            print "DBG %s"  % m
            try:
                if "STARTED" in m['data']:
                    return True
            except TypeError:
                pass
    except ConnectionError:
        print "DBG %s: not STARTED. Timeout occurred."
        return False


def wait_for_results(vm, result_id, max_minute=60):
    #r = Redis()
    r = StrictRedis(socket_timeout=max_minute * 60)

    p = r.pubsub()
    p.subscribe(vm.name)
    results = []
    log = ""
    res = ""

    # timeout
    try:
        for m in p.listen():
            print "DBG %s" % m
            try:
                if "ENDED" not in m['data']:

                    #   SAVING LOGS

                    if log is "":
                        log = str(m['data'])
                        save_logs(result_id, log)
                    else:
                        log += ", %s" % str(m['data'])
                        save_logs(result_id, log)

                    # SAVING RESULTS

                    if "+" in m['data']:
                        results.append(str(m['data']))
                        if res is not "STARTED": # or res is not "":
                            res += ", %s" % str(m['data'])
                        else:
                            res += "%s" % str(m['data'])
                        upd_record_result(result_id, result=res.replace("+ ","").strip())
                else:
                    return results
            except TypeError:
                pass
    except ConnectionError:
        print "DBG %s: Timeout occurred during execution"
        return "ERROR: Timeout occurred during execution"


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
        choices=['silent', 'melt', 'exploit', 'exploit_docx', 'exploit_ppsx', 'exploit_web',
        'mobile', 'agents', 'exploits', 'all'],
        help="Kind of test (or test case)", )
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

    if args.action == "dispatch":
        print "DBG add record to db"
        test_id = start_test()


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

    print "MASTER on %s, action %s" % (vm_names, args.action)
    r = pool.map_async(actions[args.action], [ ( n, args ) for n in vm_names ])
    results = r.get()

    # REPORT
    
    rep = Report(test_id, results)
    if args.action == "dispatch" or args.action == "revert":
        if rep.send_report_color_mail(logdir.split('/')[-1]) is False:
            print "[!] Problem sending HTML email Report!"
    else:
        if args.action == "update":
            if rep.send_mail() is False:
                print "[!] Problem sending mail!"

    os.system('sudo ./net_disable.sh')
    print "[!] Disabling NETWORKING!"
    os.system('sudo rm -fr /tmp/screenshot_*')    
    print "[!] Deleting Screenshots!"

if __name__ == "__main__":	
    main()
