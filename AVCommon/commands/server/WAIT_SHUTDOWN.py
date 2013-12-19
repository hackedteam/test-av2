__author__ = 'fabrizio'
import os
import sys
import time
from AVCommon.logger import logging
from time import sleep


def execute(vm, args):
    from AVMaster import vm_manager

    """ server side """
    #logging.debug("    CS Execute")
    assert vm, "null vm"


    for i in range (30):
        if vm_manager.execute(vm, "is_powered_off"):
            return True, "%s VM is stopped" % vm
        else:
            logging.debug("%s, not yet powered off" % vm)
            time.sleep(30)

    ret = vm_manager.execute(vm, "shutdown")
    if not ret:
        return False, "Not Stopped VM %s" % ret

    for i in range (10):
        if vm_manager.execute(vm, "is_powered_off"):
            return True, "%s VM is stopped" % vm
        else:
            logging.debug("%s, not yet powered off" % vm)
            time.sleep(30)

    return False, "%s VM isn't stopped" % vm