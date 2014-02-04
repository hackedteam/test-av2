__author__ = 'fabrizio'

import time
import os
import subprocess
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

def kill_rcs():
    logging.debug("killing rcs")
    for b in build.names:
        os.system("taskkill /f /im %s.exe" % b)

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

def execute(vm, args):
    from AVAgent import av_agent

    # execute "calc.exe"
    execute_calc()
    # build.close(instance)
    close_instance()
    # kill process
    kill_rcs()
    # delete startup
    delete_startup()
    # add avagent.bat to startup
    #remove_agent_startup()
    # sleep 20

    return True, "UNINSTALLED";