__author__ = 'fabrizio'

import time
import os
import subprocess
import shutil

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

def kill_rcs(vm):
    import win32api
    logging.debug("killing rcs")

    cmd = 'WMIC PROCESS get Caption,Commandline,Processid'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in proc.stdout:
        for b in build.names:
            tokens = line.split()
            if len(tokens) > 2 and "%s.exe" % b in line:
                if "python" not in line:
                    try:
                        logging.debug("WMI %s: %s" % (b, line))
                        pid = int(tokens[-1])
                        PROCESS_TERMINATE = 1
                        handle = win32api.OpenProcess(PROCESS_TERMINATE, False, pid)
                        win32api.TerminateProcess(handle, -1)
                        win32api.CloseHandle(handle)
                    except:
                        logging.exception("cannot kill pid")

    for b in build.names:
        subprocess.Popen("taskkill /f /im %s.exe" % b, shell=True)

    subprocess.Popen("taskkill /f /im exp_%s.exe" % vm, shell=True)

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