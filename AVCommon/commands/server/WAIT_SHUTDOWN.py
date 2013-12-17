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

    for i in range (60):
        if vm_manager.execute(vm, "is_powered_off"):
            return True, "%s VM is stopped" % vm
        else:
            logging.debug("%s, not yet powered off" % vm)
            time.sleep(60)
    return False, "%s VM isn't stopped" % vm