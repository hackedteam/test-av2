__author__ = 'fabrizio'


import os
import sys
from AVCommon.logger import logging
from time import sleep
from AVCommon import mq

def execute(vm, protocol, args):
    """ server side """
    from AVMaster import vm_manager

    #logging.debug("    CS Execute")
    assert vm, "null vm"
    mq = protocol.mq

    timeout = 30 # 300
    if args:
        timeout = args / 10

    mq.reset_connection(vm)

    cmd = "/Windows/System32/logoff.exe"
    ret = vm_manager.execute(vm, "executeCmd", cmd, [] , 10, True, True)
    logging.debug("logoff ret: %s" % ret)

    started = False
    if ret:
        for i in range(6):
            if vm_manager.execute(vm, "is_powered_on"):
                logging.debug("powered on")
                for i in range(timeout):
                    if mq.check_connection(vm):
                        logging.debug("got connection from %s" % vm)
                        return True, "Login VM"
                    sleep(10)

                logging.debug("try to reboot")
                ret = vm_manager.execute(vm, "reboot")
            else:
                sleep(10)


    return False, "Cannot relogin"