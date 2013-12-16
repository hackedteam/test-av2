__author__ = 'fabrizio'

from AVCommon.logger import logging
import time

from AVCommon import command
from AVAgent import build

from AVCommon.logger import logging


def on_init(vm, args):
    """ server side """
    return True


def on_answer(vm, success, answer):
    """ server side """
    from AVMaster import vm_manager
    cmd = "/windows/system32/calc.exe"
    arg = []
    ret = vm_manager.execute(vm, "executeCmd", cmd, arg, 40, True, True)

    #   logout

    pass

def execute_calc():
    pass

def close_instance():
    pass

def kill_rcs():
    blacklist = set(['BTHSAmpPalService','CyCpIo','CyHidWin','iSCTsysTray','quickset'])

    pass

def delete_startup():
    pass

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