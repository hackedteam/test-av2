import os
import sys
from AVCommon.logger import logging
from time import sleep


def execute(vm, args):
    """ server side """
    from AVMaster import vm_manager

    logging.debug("    CS Execute")
    assert vm, "null vm"

    ret = vm_manager.execute(vm, "startup")
    started = False
    if ret:
        for i in range(3):
            sleep(10)
            if vm_manager.execute(vm, "is_powered_on"):
                for i in range(12):
                    started = vm_manager.execute(vm, "executeCmd", "c:\\windows\\system32\\ipconfig.exe") == 0
                    logging.debug("%s, executing ipconfig, ret: %s" % (vm,started))
                    if started:
                        return True, "Started VM"
                    else:
                        sleep(60)
                if not started:
                    logging.debug("%s: reboot requested" % vm)
                    vm_manager.execute(vm, "reboot")
                    sleep(10)
                    continue

                return False, "Not started VM"
            else:
                logging.debug("%s: not yet powered" % vm)

        return False, "Error Occurred: Timeout while starting VM"
    else:
        return False, "Not Started VM"
