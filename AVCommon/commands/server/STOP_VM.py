import os
import sys
import logging
from time import sleep


def execute(vm, args):
    """ server side """
    from AVMaster import vm_manager

    logging.debug("    CS Execute")
    assert vm, "null vm"

    ret = vm_manager.execute(vm, "shutdown")
    if ret == 0:
        return True, "Stopped VM"
    else:
        return False, "Not Stopped VM"
