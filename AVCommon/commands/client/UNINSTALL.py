__author__ = 'fabrizio'

import time
import os
import subprocess
from AVCommon.logger import logging

from AVCommon import command
from AVCommon import process

from AVAgent import build

from AVCommon.logger import logging

blacklist = ['BTHSAmpPalService','CyCpIo','CyHidWin','iSCTsysTray','quickset','agent']
start_dirs = ['C:Users/avtest/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup',
            'C:/Documents and Settings/avtest/Start Menu/Programs/Startup', 'C:/Users/avtest/Desktop']

def on_init(vm, args):
    """ server side """
    return True


def on_answer(vm, success, answer):
    """ server side """
    from AVMaster import vm_manager
    cmd = "/windows/system32/logout.exe"
    arg = []
    ret = vm_manager.execute(vm, "executeCmd", cmd, arg, 40, True, True)

    #   logout

    pass

def execute_calc():
    logging.debug("executing calc")
    proc = subprocess.Popen(["calc.exe"])
    process.wait_timeout(proc, 20)
    logging.debug("killing calc")
    proc.kill()

def close_instance():
    logging.debug("closing instance")
    backend = command.context["backend"]
    build.uninstall(backend)

def kill_rcs():
    logging.debug("killing rcs")
    for b in blacklist:
        os.system("taskkill /f /im %s.exe" % b)

def delete_startup():
    logging.debug("deleting startup")
    for d in start_dirs:
        for b in blacklist:
            filename = "%s/%s.exe" %(d,b)
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    logging.exception("Cannot delete %s" % filename)

def add_agent_startup():
    pass

def execute(vm, args):
    # execute "calc.exe"
    execute_calc()
    # build.close(instance)
    close_instance()
    # kill process
    kill_rcs()
    # delete startup
    delete_startup()
    # add avagent.bat to startup
    add_agent_startup()
    # sleep 20

    return True, "UNINSTALLED";