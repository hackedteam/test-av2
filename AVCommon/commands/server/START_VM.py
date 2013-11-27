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
    started = False
    if ret:
        for i in range(6):
            sleep(10)
            if vm_manager.execute(vm, "is_powered_on"):
                for i in range(6):
                    sleep(10)
                    started = vm_manager.execute(vm, "executeCmd", "c:\\windows\\system32\\ipconfig.exe") == 0
                    logging.debug("executing ipconfig, ret: %s" % started)
                    if started:
                        return True, "Started VM"
                if not started:
                    vm_manager.execute(vm, "reboot")
                    sleep(10)
                    continue

                return False, "Not started VM"
            else:
                logging.debug("%s: not yet powered" % vm)

        return False, "Error Occurred: Timeout while starting VM"
    else:
        return False, "Not Started VM"
