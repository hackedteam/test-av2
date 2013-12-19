import os
import sys
from AVCommon.logger import logging
from time import sleep


def execute(vm, protocol, args):
    from AVMaster import vm_manager

    """ server side """
    clean = True # VM IS NOT INFECTED!! TEST CAN CONTINUE!!!

    #logging.debug("    CS Execute")
    assert vm, "null vm"

    blacklist = ['BTHSAmpPalService','CyCpIo','CyHidWin','iSCTsysTray','quickset']

    dirs = ['C:Users/avtest/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup',
            'C:/Documents and Settings/avtest/Start Menu/Programs/Startup', 'C:/Users/avtest/Desktop']

    for d in dirs:
        out = vm_manager.execute(vm, "listDirectoryInGuest", d)
        #logging.debug("listDirectoryInGuest: %s" % out)

        for b in blacklist:
            if b in out:
                logging.info("%s, found %s in %s" % (vm, b, d))
                clean = False
                break

    if clean is True:
        return True, "VM is not infected"
    else:
        return False, "VM is INFECTED"
