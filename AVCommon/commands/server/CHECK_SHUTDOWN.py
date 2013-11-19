import os
import sys
import logging
from time import sleep

from AVMaster import vm_manager

def execute(vm, args):
    """ server side """
    logging.debug("    CS Execute")
    assert vm, "null vm"

    if vm_manager.execute(vm, "is_powered_off"):
        return True, "%s VM is stopped" % vm
    return False, "%s VM isn't stopped" % vm
