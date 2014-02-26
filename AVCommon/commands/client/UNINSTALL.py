__author__ = 'fabrizio'

import time
import os
import subprocess
import shutil
import re

from AVCommon.logger import logging

from AVCommon import command
from AVCommon import process

from AVAgent import build

from AVCommon.logger import logging
from AVAgent import build


def on_init(vm, args):
    """ server side """
    return True


def on_answer(vm, success, answer):
    """ server side """
    from AVMaster import vm_manager
    cmd = "/windows/system32/logout.exe"
    arg = []
    ret = vm_manager.execute(vm, "executeCmd", cmd, arg, 40, True, True)

def execute_calc():
    logging.debug("executing calc")
    proc = subprocess.Popen(["calc.exe"])
    process.wait_timeout(proc, 20)
    logging.debug("killing calc")
    proc.kill()

def close_instance():
    try:
        logging.debug("closing instance")
        backend = command.context["backend"]
        build.uninstall(backend)
    except:
        logging.exception("Cannot close instance")


def kill_pid(pid):
    import win32api

    PROCESS_TERMINATE = 1
    handle = win32api.OpenProcess(PROCESS_TERMINATE, False, pid)
    win32api.TerminateProcess(handle, -1)
    win32api.CloseHandle(handle)


def kill_proc_by_regex(proc, reagent):
    for line in proc.stdout:
        tokens = line.split()
        if len(tokens) < 2:
            continue

        if reagent.match(line):
            try:
                logging.debug("WMI %s: %s" % (exename, line))
                pid = int(tokens[-1])
                kill_pid(pid)
            except:
                logging.exception("cannot kill pid")

        for b in build.names:
            exename = "%s.exe" % b

            if exename in line and "python" not in line:
                try:
                    logging.debug("WMI %s: %s" % (exename, line))
                    pid = int(tokens[-1])
                    kill_pid(pid)
                except:
                    logging.exception("cannot kill pid")


def kill_rcs(vm):

    logging.debug("killing rcs")

    cmd = 'WMIC PROCESS get Caption,Commandline,Processid'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    expname = "exp_%s" % vm
    if expname not in build.names:
        build.names.append(expname)
        build.names.append("notepad")

    reagent = re.compile(r'.*agent.*\.exe')
    kill_proc_by_regex(proc, reagent)

    reagent = re.compile(r'.*%s_\w*\.exe' % expname)
    kill_proc_by_regex(proc, reagent)

    for b in build.names:
        subprocess.Popen("taskkill /f /im %s.exe" % b, shell=True)

    tasklist =  subprocess.Popen(["tasklist"], stdout=subprocess.PIPE).communicate()[0]
    logging.debug(tasklist)

def delete_startup():
    logging.debug("deleting startup")
    for d in build.start_dirs:
        for b in build.names:
            filename = "%s/%s.exe" %(d,b)
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    logging.exception("Cannot delete %s" % filename)

def remove_agent_startup():
    startup_dir = 'C:/Users/avtest/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup'
    remote_name = "%s/av_agent.bat" % startup_dir
    if os.path.exists(remote_name):
        os.remove(remote_name)

def delete_build():
    logging.debug("deleting build")
    if os.path.exists("build"):
        shutil.rmtree("build")

def execute(vm, args):
    from AVAgent import av_agent

    # execute "calc.exe"
    execute_calc()
    # build.close(instance)
    close_instance()
    # kill process
    kill_rcs(vm)
    # delete startup
    delete_startup()
    # add avagent.bat to startup
    #remove_agent_startup()
    # sleep 20
    delete_build()

    return True, "UNINSTALLED";