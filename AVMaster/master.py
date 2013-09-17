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
from lib.web.models import db, Test, Result, Sample
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
        print "DBG %s: not STARTED. Timeout occurred." % vm
        return False

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
    global db

    try:
        timestamp = time.strftime("%Y%m%d_%H%M", time.gmtime())
        
        t = Test(0,str(timestamp))
        db.session.add(t)
        db.session.commit()
        return t
    except Exception as e:
        print "DBG error inserting report in db. Exception: %s" % e
        print DB_PATH
        return None

def end_test(test):
    try:
        #t = Test.query.filter_by(id=t_id)
        if test is None:
            return False
        test.status = 1
        db.session.add(test)
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
            max_minute = 45
        elif kind == "exploit":
            max_minute = 20
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

        # GROUP OF TESTS Implementation

        if kind == "agents":
            results.append( dispatch_kind(vm_name, "silent", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "mobile", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "exploit_docx", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "exploit_web", args) )
        elif kind == "silentmelt":
            results.append( dispatch_kind(vm_name, "silent", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "melt", args) )
        elif kind == "release":
            results.append( dispatch_kind(vm_name, "silent", args) )
            sleep(random.randint(5,10))
            results.append( dispatch_kind(vm_name, "melt", args) )
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
            results.append( dispatch_kind(vm_name, "exploit", args) )
            sleep(random.randint(5,10))
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

def dispatch_kind(vm_name, kind, args, r_id=None, tries=0):

    #   PREPARE FILES

    global status, test_id

    print "DBG test_id is %s" % test_id

    delay = len(args.vms)

    test_dir_7  = "C:\\Users\\avtest\\Desktop\\AVTEST"
#    test_dir_xp = "C:\\Documents and Settings\\avtest\\Desktop\\AVTEST"

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

    if kind == "mobile" or kind == "silent":
        filestocopy.append("assets/codec")
        filestocopy.append("assets/codec_mod")
        filestocopy.append("assets/sqlite")
        filestocopy.append("assets/sqlite_mod")

    res = "%s, %s, ERROR GENERAL" % (vm_name, kind)

    vm = VMachine(vm_conf_file, vm_name)
    job_log(vm.name, "DISPATCH %s" % kind)

    #   STARTUP VM

    if tries <= 0:
        vm.revert_last_snapshot()
        job_log(vm.name, "REVERTED")
        sleep(random.randint(30, delay * 30))
    elif tries == 10:
        return "%s, %s, ERROR not started after 10 tries." % (vm_name, kind)
    else:
        vm.shutdown()
        while vm.is_powered_off() is False:
            sleep(5)

    vm.startup()
    job_log(vm.name, "STARTUP")

    #   OPEN CHANNEL

    if kind == "silent" or kind == "melt":
        max_minute = 45
    elif kind == "exploit":
        max_minute = 20
    elif kind == "mobile" or "exploit_" in kind:
        max_minute = 5  

    r = StrictRedis(socket_timeout=max_minute * 60)
    p = r.pubsub()
    p.subscribe(vm.name)

    started = False
    results = []
    log = ""
    res = ""

    try:
        for m in p.listen():
            print "DBG %s: %s"  % (m['channel'], m['data'])
            try:
                if started is False:
                    if "STARTED" in m['data']: # and started is False:
                        started = True

                        # PREPARE ENVIRONMENT

                        if r_id is None:
                            result_id = add_record_result(vm_name, kind, test_id, status, "STARTED")
                        else:
                            result_id = r_id
                        print "DBG %s added result with id %s" % (vm_name,result_id)

                        job_log(vm_name, "LOGGED")
                        test_dir = test_dir_7
                        copy_to_guest(vm, test_dir, filestocopy)

                        job_log(vm_name, "ENVIRONMENT")
                        upd_record_result(result_id, result="ENVIRONMENT")

                        # EXECUTE 
                        
                        vmman.executeCmd(vm, "%s\\%s" % (test_dir, buildbat), interactive=True, bg=True)

                        # CHECK FOR ERROR IN EXECUTION

                        sleep(3)
                        out = vmman.listProcesses(vm)
                        found = False
                        tick = 0
                        script_name = "build_%s_minotauro.bat" % kind
                        print "DBG script to find is %s" % script_name

                        while tick <= 5:
                            if "python.exe" in out or script_name in out or "cmd.exe" in out:
                                found = True
                                print "DBG process found for %s!" % vm_name
                            if found == True:
                                break
                            print "DBG Python.EXE not found for %s. sleeping 5 secs (retry %d)" % (vm_name, tick)
                            print "DBG processes:\n%s" % out
                            tick+=1
                            sleep(5)

                        if found == False:
                            tries+=1
                            print "%s STARTED but not EXECUTED. Retry %d setup" % (vm_name, tries)
                            return dispatch_kind(vm_name, kind, args, result_id, tries)

                        job_log(vm_name, "EXECUTED %s" % kind)
                        upd_record_result(result_id, result="EXECUTED")

                else: # started is True

                    if "ENDED" not in m['data']: # and started is True:

                        #   SAVING LOGS

                        if log is "":
                            log = str(m['data'])
                            save_logs(result_id, log)
                        else:
                            log += ", %s" % str(m['data'])
                            save_logs(result_id, log)

                        # SAVING CURRENT RESULT

                        if "+" in m['data']:
                            results.append(str(m['data']))
                            if "STARTED" not in res: # or res is not "":
                                res += ", %s" % str(m['data'])
                            else:
                                res += "%s" % str(m['data'])
                            upd_record_result(result_id, result=res.replace("+ ","").strip())
                        
                        if "FAILED SCOUT BUILD" in m['data'] or "FAILED SCOUT EXECUTE" in m['data']:

                            # SAVING SAMPLE

                            test_dir = "C:\\Users\\avtest\\Desktop\\AVTEST\\build"
                            platform = m['data'].split(" ")[-1].split("\\")[-2]
                            build_zip_src = "%s\\%s\\build.zip" % (test_dir, platform)
                            build_zip_dst = "tmp/detected_%s.zip" % vm
                            print "DBG copying %s to %s" % (build_zip_src, build_zip_dst)
                            vm.get_file(build_zip_src, build_zip_dst)
                            #vmman.copyFileFromGuest(vm, build_zip_src, build_zip_dst)
                            print "DBG adding record sample"
                            a = add_record_sample(result_id, build_zip_dst)
                            if a:
                                print "sample SAVED on db"
                                #os.system('sudo rm -fr %s') % build_zip_dst
                            else:
                                print "sample NOT SAVED on db"
                    else:
                        print "DBG [%s] passing debug files txt from host" % vm.name
                        res_txt_dst = "%s/results_%s_%s.txt" % (logdir, vm, kind)
                        res_txt_src = "C:\\Users\\avtest\\Desktop\\AVTEST\\results.txt"
                        vm.get_file(res_txt_src, res_txt_dst)

                        print "DBG results are %s" % results

                        job_log(vm_name, "SAVED %s" % kind)
                        
                        #execute(vm, test_id, result_id, "%s\\%s" % (test_dir, buildbat), kind)

                        #timestamp = time.strftime("%Y%m%d_%H%M", time.gmtime())
                        if save_screenshot(vm, result_id) is True:
                            job_log(vm_name, "SCREENSHOT ok")
                            
                        # suspend & refresh snapshot
                        #vm.suspend()
                        vm.shutdown()
                        job_log(vm_name, "SUSPENDED %s" % kind)

    #                    return results # should be: vm_name, kind, results
                        return "%s, %s, %s" % (vm_name, kind, res.split(",")[-1].replace("+ ",""))
            except TypeError:
                pass
    except ConnectionError:
        if started is False:
            tries+=1
            print "DBG %s: not STARTED. Timeout occurred." % vm
            return dispatch_kind(vm_name, kind, args, None, tries)
        else:
            tries+=1
            print "DBG %s: Timeout occurred during execution" % vm
            return dispatch_kind(vm_name, kind, args, result_id, tries)

def push(flargs):
    vm_name, args = flargs
    kind = args.kind
    
    vm = VMachine(vm_conf_file, vm_name)

    if vm.is_powered_on():
        print "[!] %s is already powered on. please shutdown vm before." % vm_name
        return "%s not pushed %s" % (vm_name, kind)

    job_log(vm_name, "PUSH %s" % kind)
        
    vm.revert_last_snapshot()
    job_log(vm_name, "REVERTED")

    sleep(random.randint(30, 60))
    vm.startup()
    job_log(vm_name, "STARTUP")
    
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

    result = "%s, ERROR GENERAL" % vm_name
    """
    if wait_for_startup(vm) is False:
        result = "ERROR wait for startup for %s" % vm_name 
    else:
        copy_to_guest(vm, test_dir, filestocopy)
        job_log(vm_name, "ENVIRONMENT")
        result = "%s, pushed %s." % (vm_name, kind)
    """
    r = StrictRedis(socket_timeout=5 * 60)
    p = r.pubsub()
    p.subscribe(vm_name)

    try:
        for m in p.listen():
            try:
                print "DBG %s: %s"  % (m['channel'], m['data'])
                if "STARTED" in m['data']: # and started is False:
                    copy_to_guest(vm, test_dir, filestocopy)
                    job_log(vm_name, "ENVIRONMENT")
                    return "%s, pushed %s." % (vm_name, kind)
            except TypeError:
                pass
    except ConnectionError:
                print "DBG %s: not STARTED. Timeout occurred." % vm_name
                return push(flargs)    

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

def do_test(flargs):
    '''
    results = [['fakeav, silent, STARTED', 
        'fakeav, melt, ERROR', 
        'fakeav, exploit, SUCCESS', 
        'fakeav, exploit_ppsx, FAILED']]

    rep = Report(9999, results)
    if rep.send_report_color_mail("reportz") is False:
        print "[!] Problem sending HTML email Report!"
    '''
#    results = [['360cn, silent, + SUCCESS ELITE BLACKLISTED', '360cn, melt, + SUCCESS SCOUT SYNC', '360cn, exploit_docx, + SUCCESS EXPLOIT SAVE', '360cn, exploit_web, + SUCCESS EXPLOIT SAVE', '360cn, mobile, + SUCCESS PULL android'], ['avast, silent, + SUCCESS ELITE UNINSTALLED', 'avast, melt, + SUCCESS SCOUT SYNC', 'avast, exploit_docx, + SUCCESS EXPLOIT SAVE', 'avast, exploit_web, + SUCCESS EXPLOIT SAVE', 'avast, mobile, + SUCCESS PULL android'], ['avira, silent, + SUCCESS ELITE UNINSTALLED', 'avira, melt, + SUCCESS SCOUT SYNC', 'avira, exploit_docx, + SUCCESS EXPLOIT SAVE', 'avira, exploit_web, + SUCCESS EXPLOIT SAVE', 'avira, mobile, + SUCCESS PULL android'], ['avg, silent, + SUCCESS ELITE BLACKLISTED', 'avg, melt, + SUCCESS SCOUT SYNC', 'avg, exploit_docx, + SUCCESS EXPLOIT SAVE', 'avg, exploit_web, + SUCCESS EXPLOIT SAVE', 'avg, mobile, + SUCCESS PULL android'], ['ahnlab, silent, + SUCCESS ELITE UNINSTALLED', 'ahnlab, melt, + SUCCESS SCOUT SYNC', 'ahnlab, exploit_docx, + SUCCESS EXPLOIT SAVE', 'ahnlab, exploit_web, + SUCCESS EXPLOIT SAVE', 'ahnlab, mobile, + SUCCESS PULL android'], ['adaware, silent, + SUCCESS ELITE UNINSTALLED', 'adaware, melt, + SUCCESS SCOUT SYNC', 'adaware, exploit_docx, + SUCCESS EXPLOIT SAVE', 'adaware, exploit_web, + SUCCESS EXPLOIT SAVE', 'adaware, mobile, + SUCCESS PULL android'], ['avg32, silent, + SUCCESS ELITE BLACKLISTED', 'avg32, melt, + SUCCESS SCOUT SYNC', 'avg32, exploit_docx, + SUCCESS EXPLOIT SAVE', 'avg32, exploit_web, + SUCCESS EXPLOIT SAVE', 'avg32, mobile, + SUCCESS PULL android'], ['avast32, silent, + SUCCESS ELITE UNINSTALLED', 'avast32, melt, + SUCCESS SCOUT SYNC', 'avast32, exploit_docx, + SUCCESS EXPLOIT SAVE', 'avast32, exploit_web, + SUCCESS EXPLOIT SAVE', 'avast32, mobile, + SUCCESS PULL android'], ['bitdef, silent, + SUCCESS ELITE BLACKLISTED', 'bitdef, melt, + FAILED SCOUT SYNC', 'bitdef, exploit_docx, + SUCCESS EXPLOIT SAVE', 'bitdef, exploit_web, + SUCCESS EXPLOIT SAVE', 'bitdef, mobile, + SUCCESS PULL android'], ['comodo, silent, + SUCCESS ELITE BLACKLISTED', 'comodo, melt, + SUCCESS SCOUT SYNC', 'comodo, exploit_docx, + SUCCESS EXPLOIT SAVE', 'comodo, exploit_web, + SUCCESS EXPLOIT SAVE', 'comodo, mobile, + SUCCESS PULL android'], ['drweb, silent, + SUCCESS ELITE BLACKLISTED', 'drweb, melt, + SUCCESS SCOUT SYNC', 'drweb, exploit_docx, + SUCCESS EXPLOIT SAVE', 'drweb, exploit_web, + SUCCESS EXPLOIT SAVE', 'drweb, mobile, + SUCCESS PULL android'], ['eset, silent, + SUCCESS ELITE UNINSTALLED', 'eset, melt, + SUCCESS SCOUT SYNC', 'eset, exploit_docx, + SUCCESS EXPLOIT SAVE', 'eset, exploit_web, + SUCCESS EXPLOIT SAVE', 'eset, mobile, + SUCCESS PULL android'], ['fsecure, silent, + SUCCESS ELITE UNINSTALLED', 'fsecure, melt, + SUCCESS SCOUT SYNC', 'fsecure, exploit_docx, + SUCCESS EXPLOIT SAVE', 'fsecure, exploit_web, + SUCCESS EXPLOIT SAVE', 'fsecure, mobile, + SUCCESS PULL android'], ['gdata, silent, + SUCCESS ELITE BLACKLISTED', 'gdata, melt, + SUCCESS SCOUT SYNC', 'gdata, exploit_docx, + SUCCESS EXPLOIT SAVE', 'gdata, exploit_web, + SUCCESS EXPLOIT SAVE', 'gdata, mobile, + SUCCESS PULL android'], ['kis, silent, + SUCCESS ELITE UNINSTALLED', 'kis, melt, + SUCCESS SCOUT SYNC', 'kis, exploit_docx, + SUCCESS EXPLOIT SAVE', 'kis, exploit_web, + SUCCESS EXPLOIT SAVE', 'kis, mobile, + SUCCESS PULL android'], ['kis32, silent, + SUCCESS ELITE BLACKLISTED', 'kis32, melt, + SUCCESS SCOUT SYNC', 'kis32, exploit_docx, + SUCCESS EXPLOIT SAVE', 'kis32, exploit_web, + SUCCESS EXPLOIT SAVE', 'kis32, mobile, + SUCCESS PULL android'], ['mcafee, silent, + SUCCESS ELITE UNINSTALLED', 'mcafee, melt, + SUCCESS SCOUT SYNC', 'mcafee, exploit_docx, + SUCCESS EXPLOIT SAVE', 'mcafee, exploit_web, + SUCCESS EXPLOIT SAVE', 'mcafee, mobile, + SUCCESS PULL android'], ['msessential, silent, + SUCCESS ELITE UNINSTALLED', 'msessential, melt, + SUCCESS SCOUT SYNC', 'msessential, exploit_docx, + SUCCESS EXPLOIT SAVE', 'msessential, exploit_web, + SUCCESS EXPLOIT SAVE', 'msessential, mobile, + SUCCESS PULL android'], ['mbytes, silent, + SUCCESS ELITE UNINSTALLED', 'mbytes, melt, + SUCCESS SCOUT SYNC', 'mbytes, exploit_docx, + SUCCESS EXPLOIT SAVE', 'mbytes, exploit_web, + SUCCESS EXPLOIT SAVE', 'mbytes, mobile, + SUCCESS PULL android'], ['norton, silent, + SUCCESS ELITE UNINSTALLED', 'norton, melt, + SUCCESS SCOUT SYNC', 'norton, exploit_docx, + SUCCESS EXPLOIT SAVE', 'norton, exploit_web, + SUCCESS EXPLOIT SAVE', 'norton, mobile, + SUCCESS PULL android'], ['norman, silent, n', 'norman, melt, + SUCCESS SCOUT SYNC', 'norman, exploit_docx, + SUCCESS EXPLOIT SAVE', 'norman, exploit_web, + SUCCESS EXPLOIT SAVE', 'norman, mobile, + SUCCESS PULL android'], ['panda, silent, + SUCCESS ELITE UNINSTALLED', 'panda, melt, + SUCCESS SCOUT SYNC', 'panda, exploit_docx, + SUCCESS EXPLOIT SAVE', 'panda, exploit_web, + SUCCESS EXPLOIT SAVE', 'panda, mobile, + SUCCESS PULL android'], ['pctools, silent, + SUCCESS ELITE UNINSTALLED', 'pctools, melt, + SUCCESS SCOUT SYNC', 'pctools, exploit_docx, + SUCCESS EXPLOIT SAVE', 'pctools, exploit_web, + SUCCESS EXPLOIT SAVE', 'pctools, mobile, + SUCCESS PULL android'], ['risint, silent, + SUCCESS ELITE UNINSTALLED', 'risint, melt, + SUCCESS SCOUT SYNC', 'risint, exploit_docx, + SUCCESS EXPLOIT SAVE', 'risint, exploit_web, + SUCCESS EXPLOIT SAVE', 'risint, mobile, + SUCCESS PULL android'], ['sophos, silent, + SUCCESS ELITE BLACKLISTED', 'sophos, melt, + SUCCESS SCOUT SYNC', 'sophos, exploit_docx, + SUCCESS EXPLOIT SAVE', 'sophos, exploit_web, + SUCCESS EXPLOIT SAVE', 'sophos, mobile, + SUCCESS PULL android'], ['trendm, silent, + SUCCESS ELITE UNINSTALLED', 'trendm, melt, + SUCCESS SCOUT SYNC', 'trendm, exploit_docx, + SUCCESS EXPLOIT SAVE', 'trendm, exploit_web, + SUCCESS EXPLOIT SAVE', 'trendm, mobile, + SUCCESS PULL android'], ['zoneal, silent, + SUCCESS ELITE UNINSTALLED', 'zoneal, melt, + SUCCESS SCOUT SYNC', 'zoneal, exploit_docx, + SUCCESS EXPLOIT SAVE', 'zoneal, exploit_web, + SUCCESS EXPLOIT SAVE', 'zoneal, mobile, + SUCCESS PULL android']]
#    results = [['360cn, silent, + SUCCESS ELITE BLACKLISTED', '360cn, melt, + SUCCESS SCOUT SYNC', '360cn, exploit_docx, + SUCCESS EXPLOIT SAVE', '360cn, exploit_web, + SUCCESS EXPLOIT SAVE', '360cn, mobile, + SUCCESS PULL android'], ['avast, silent, + SUCCESS ELITE UNINSTALLED', 'avast, melt, + SUCCESS SCOUT SYNC', 'avast, exploit_docx, + SUCCESS EXPLOIT SAVE', 'avast, exploit_web, + SUCCESS EXPLOIT SAVE', 'avast, mobile, + SUCCESS PULL android'], ['avira, silent, + SUCCESS ELITE UNINSTALLED', 'avira, melt, + SUCCESS SCOUT SYNC', 'avira, exploit_docx, + SUCCESS EXPLOIT SAVE', 'avira, exploit_web, + SUCCESS EXPLOIT SAVE', 'avira, mobile, + SUCCESS PULL android'], ['avg, silent, + SUCCESS ELITE BLACKLISTED', 'avg, melt, + SUCCESS SCOUT SYNC', 'avg, exploit_docx, + SUCCESS EXPLOIT SAVE', 'avg, exploit_web, + SUCCESS EXPLOIT SAVE', 'avg, mobile, + SUCCESS PULL android'], ['ahnlab, silent, + SUCCESS ELITE UNINSTALLED', 'ahnlab, melt, + SUCCESS SCOUT SYNC', 'ahnlab, exploit_docx, + SUCCESS EXPLOIT SAVE', 'ahnlab, exploit_web, + SUCCESS EXPLOIT SAVE', 'ahnlab, mobile, + SUCCESS PULL android'], ['adaware, silent, + SUCCESS ELITE UNINSTALLED', 'adaware, melt, + SUCCESS SCOUT SYNC', 'adaware, exploit_docx, + SUCCESS EXPLOIT SAVE', 'adaware, exploit_web, + SUCCESS EXPLOIT SAVE', 'adaware, mobile, + SUCCESS PULL android'], ['avg32, silent, + SUCCESS ELITE BLACKLISTED', 'avg32, melt, + SUCCESS SCOUT SYNC', 'avg32, exploit_docx, + SUCCESS EXPLOIT SAVE', 'avg32, exploit_web, + SUCCESS EXPLOIT SAVE', 'avg32, mobile, + SUCCESS PULL android'], ['avast32, silent, + SUCCESS ELITE UNINSTALLED', 'avast32, melt, + SUCCESS SCOUT SYNC', 'avast32, exploit_docx, + SUCCESS EXPLOIT SAVE', 'avast32, exploit_web, + SUCCESS EXPLOIT SAVE', 'avast32, mobile, + SUCCESS PULL android'], ['bitdef, silent, + SUCCESS ELITE BLACKLISTED', 'bitdef, melt, + FAILED SCOUT SYNC', 'bitdef, exploit_docx, + SUCCESS EXPLOIT SAVE', 'bitdef, exploit_web, + SUCCESS EXPLOIT SAVE', 'bitdef, mobile, + SUCCESS PULL android'], ['comodo, silent, + SUCCESS ELITE BLACKLISTED', 'comodo, melt, + SUCCESS SCOUT SYNC', 'comodo, exploit_docx, + SUCCESS EXPLOIT SAVE', 'comodo, exploit_web, + SUCCESS EXPLOIT SAVE', 'comodo, mobile, + SUCCESS PULL android'], ['drweb, silent, + SUCCESS ELITE BLACKLISTED', 'drweb, melt, + SUCCESS SCOUT SYNC', 'drweb, exploit_docx, + SUCCESS EXPLOIT SAVE', 'drweb, exploit_web, + SUCCESS EXPLOIT SAVE', 'drweb, mobile, + SUCCESS PULL android'], ['eset, silent, + SUCCESS ELITE UNINSTALLED', 'eset, melt, + SUCCESS SCOUT SYNC', 'eset, exploit_docx, + SUCCESS EXPLOIT SAVE', 'eset, exploit_web, + SUCCESS EXPLOIT SAVE', 'eset, mobile, + SUCCESS PULL android'], ['fsecure, silent, + SUCCESS ELITE UNINSTALLED', 'fsecure, melt, + SUCCESS SCOUT SYNC', 'fsecure, exploit_docx, + SUCCESS EXPLOIT SAVE', 'fsecure, exploit_web, + SUCCESS EXPLOIT SAVE', 'fsecure, mobile, + SUCCESS PULL android'], ['gdata, silent, + SUCCESS ELITE BLACKLISTED', 'gdata, melt, + SUCCESS SCOUT SYNC', 'gdata, exploit_docx, + SUCCESS EXPLOIT SAVE', 'gdata, exploit_web, + SUCCESS EXPLOIT SAVE', 'gdata, mobile, + SUCCESS PULL android'], ['kis, silent, + SUCCESS ELITE UNINSTALLED', 'kis, melt, + SUCCESS SCOUT SYNC', 'kis, exploit_docx, + SUCCESS EXPLOIT SAVE', 'kis, exploit_web, + SUCCESS EXPLOIT SAVE', 'kis, mobile, + SUCCESS PULL android'], ['kis32, silent, + SUCCESS ELITE BLACKLISTED', 'kis32, melt, + SUCCESS SCOUT SYNC', 'kis32, exploit_docx, + SUCCESS EXPLOIT SAVE', 'kis32, exploit_web, + SUCCESS EXPLOIT SAVE', 'kis32, mobile, + SUCCESS PULL android'], ['mcafee, silent, + SUCCESS ELITE UNINSTALLED', 'mcafee, melt, + SUCCESS SCOUT SYNC', 'mcafee, exploit_docx, + SUCCESS EXPLOIT SAVE', 'mcafee, exploit_web, + SUCCESS EXPLOIT SAVE', 'mcafee, mobile, + SUCCESS PULL android'], ['msessential, silent, + SUCCESS ELITE UNINSTALLED', 'msessential, melt, + SUCCESS SCOUT SYNC', 'msessential, exploit_docx, + SUCCESS EXPLOIT SAVE', 'msessential, exploit_web, + SUCCESS EXPLOIT SAVE', 'msessential, mobile, + SUCCESS PULL android'], ['mbytes, silent, + SUCCESS ELITE UNINSTALLED', 'mbytes, melt, + SUCCESS SCOUT SYNC', 'mbytes, exploit_docx, + SUCCESS EXPLOIT SAVE', 'mbytes, exploit_web, + SUCCESS EXPLOIT SAVE', 'mbytes, mobile, + SUCCESS PULL android'], ['norton, silent, + SUCCESS ELITE UNINSTALLED', 'norton, melt, + SUCCESS SCOUT SYNC', 'norton, exploit_docx, + SUCCESS EXPLOIT SAVE', 'norton, exploit_web, + SUCCESS EXPLOIT SAVE', 'norton, mobile, + SUCCESS PULL android'], ['norman, silent, n', 'norman, melt, + SUCCESS SCOUT SYNC', 'norman, exploit_docx, + SUCCESS EXPLOIT SAVE', 'norman, exploit_web, + SUCCESS EXPLOIT SAVE', 'norman, mobile, + SUCCESS PULL android'], ['panda, silent, + SUCCESS ELITE UNINSTALLED', 'panda, melt, + SUCCESS SCOUT SYNC', 'panda, exploit_docx, + SUCCESS EXPLOIT SAVE', 'panda, exploit_web, + SUCCESS EXPLOIT SAVE', 'panda, mobile, + SUCCESS PULL android'], ['pctools, silent, + SUCCESS', 'pctools, melt, + SUCCESS', 'pctools, exploit_docx, + SUCCESS', 'pctools, exploit_web, + SUCCESS', 'pctools, mobile, SUCCESS']] #, ['risint, silent, + SUCCESS ELITE UNINSTALLED', 'risint, melt, + SUCCESS SCOUT SYNC', 'risint, exploit_docx, + SUCCESS EXPLOIT SAVE', 'risint, exploit_web, + SUCCESS EXPLOIT SAVE', 'risint, mobile, + SUCCESS PULL android'], ['sophos, silent, + SUCCESS ELITE BLACKLISTED', 'sophos, melt, + SUCCESS SCOUT SYNC', 'sophos, exploit_docx, + SUCCESS EXPLOIT SAVE', 'sophos, exploit_web, + SUCCESS EXPLOIT SAVE', 'sophos, mobile, + SUCCESS PULL android'], ['trendm, silent, + SUCCESS ELITE UNINSTALLED', 'trendm, melt, + SUCCESS SCOUT SYNC', 'trendm, exploit_docx, + SUCCESS EXPLOIT SAVE', 'trendm, exploit_web, + SUCCESS EXPLOIT SAVE', 'trendm, mobile, + SUCCESS PULL android'], ['zoneal, silent, + SUCCESS ELITE UNINSTALLED', 'zoneal, melt, + SUCCESS SCOUT SYNC', 'zoneal, exploit_docx, + SUCCESS EXPLOIT SAVE', 'zoneal, exploit_web, + SUCCESS EXPLOIT SAVE', 'zoneal, mobile, + SUCCESS PULL android']]
#    rep = Report(42, results)
    #print rep.results
#    if rep.send_report_color_mail("rep") is False:
#        print "[!] Problem sending HTML email Report!"

#    for result in rep.results:
#        print "%s: %s" % (result.vm_name,result.result)

    vm_name = "gdata"
    vm = VMachine(vm_conf_file, vm_name)
    out = vmman.listProcesses(vm)
    if "msdtc.exe" in out:
        print "found"
    else: print "not found"
    print "end test"

def add_record_sample(result_id, build_zip_dst):
    print "DBG Saving Sample"
    if not os.path.exists(build_zip_dst):
        return False
    with open(build_zip_dst, 'rb') as f:
        sample = Sample(result_id, f.read())
        db.session.add(sample)
        db.session.commit()
    return True

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
        'mobile', 'agents', 'exploits', 'silentmelt', 'release', 'all'],
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
    vSphere.username = "%s\\%s" % (c.get("vsphere", "domain"),c.get("vsphere", "user"))
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
        do_test(args)
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
        test = start_test()
        if test.id is not None:
            test_id = test.id
        else:
            print "[!] Problems with DB insert. QUITTING!"
            return

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

#    print "Finalizing test."
#    if end_test(test) is False:
#        print "[!] problem updating test status!"

    # REPORT
    
    rep = Report(test_id, results)
    if args.action == "dispatch": 
        if rep.send_report_color_mail(logdir.split('/')[-1]) is False:
            print "[!] Problem sending HTML email Report!"
        end_test(test)
    else:
        if args.action == "update": # or args.action == "revert":
            if rep.send_mail() is False:
                print "[!] Problem sending mail!"

    os.system('sudo ./net_disable.sh')
    print "[!] Disabling NETWORKING!"
    os.system('sudo rm -fr /tmp/screenshot_*')    
    print "[!] Deleting Screenshots!"

if __name__ == "__main__":	
    main()
