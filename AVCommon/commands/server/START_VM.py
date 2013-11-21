import os
import sys
import logging
from time import sleep


def execute(vm, args):
    """ server side """
    from AVMaster import vm_manager

    logging.debug("    CS Execute")
    assert vm, "null vm"

    ret = vm_manager.execute(vm, "startup")
    boot = False
    if ret:
        for i in range(6):
            if vm_manager.execute(vm, "is_powered_on"):
                while not boot:
                    sleep(10)
                    boot = vm_manager.execute(vm, "executeCmd", "c:\\windows\\system32\\ipconfig.exe") == 0
                    logging.debug("executing ipconfig, ret: %s" % ret)

                return True, "Started VM"

        return False, "Error Occurred: Timeout while starting VM"
    else:
        return False, "Not Started VM"
