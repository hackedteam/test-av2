import os
import sys
from AVCommon.logger import logging
from time import sleep


def execute(vm, protocol, args):
    """ server side """
    from AVMaster import vm_manager

    #logging.debug("    CS Execute")
    assert vm, "null vm"
    tick = 15
    if args:
        assert isinstance(args, int), "you must specify an int for timeout."

        timeout = args
        off = False


        logging.debug("%s, shutting down with timeout %s." % (vm,timeout))

        vm_manager.execute(vm, "executeCmd","C:/Windows/System32/shutdown.exe",["/s", "/t", "30"], timeout, False, True)

        for i in range(0, timeout, tick):
            sleep(tick)
            if vm_manager.execute(vm, "is_powered_off"):
                return True, "Stopped VM"


    logging.info("Forcing shutdown")
    ret = vm_manager.execute(vm, "shutdown")

    logging.debug("%s, shutdown returns: %s" % (vm, ret))

    for i in range(10):
        if vm_manager.execute(vm, "is_powered_off"):
            return True, "Stopped VM"
        sleep(tick)

    return False, "Cannot stop VM"
