import os
import sys
from AVCommon.logger import logging
from time import sleep


def execute(vm, args):
    from AVMaster import vm_manager

    """ server side """
    logging.debug("    CS Execute")
    assert vm, "null vm"

    if vm_manager.execute(vm, "is_powered_off"):
        return True, "%s VM is stopped" % vm
    return False, "%s VM isn't stopped" % vm
