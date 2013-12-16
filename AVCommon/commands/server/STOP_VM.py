import os
import sys
from AVCommon.logger import logging
from time import sleep


def execute(vm, args):
    """ server side """
    from AVMaster import vm_manager

    #logging.debug("    CS Execute")
    assert vm, "null vm"

    if args:
        assert isinstance(args, int), "you must specify an int for timeout."

        timeout = args
        off = False
        tick = 15

        logging.info("shutting down with timeout %s." % timeout)

        vm_manager.execute(vm, "executeCmd","C:/Windows/System32/shutdown.exe",["/s"], timeout, False, True)

        for i in range(0,timeout,tick):
            sleep(tick)
            if vm_manager.execute(vm, "is_powered_off"):
                off = True
                break

        if off:
            return True, "Stopped VM"
        else:
            ret = vm_manager.execute(vm, "shutdown")
            if ret:
                return True, "Stopped VM"
            else:
                return False, "Not Stopped VM %s" % ret
    else:
        ret = vm_manager.execute(vm, "shutdown")

        if ret:
            return True, "Stopped VM"
        else:
            return False, "Not Stopped VM %s" % ret
