import os
import sys
import logging
from time import sleep

from AVMaster import vm_manager

def execute(vm, args):
    """ server side """
    logging.debug("    CS Execute")
    assert vm, "null vm"

    ret = vm_manager.execute(vm, "startup")
    if ret:
        for i in range(0,6):
            if vm_manager.execute(vm, "is_powered_on"):
                return True, "Started VM"
            sleep(10)
        return False, "Error Occurred: Timeout while starting VM"
    else:
        return False, "Not Started VM"
