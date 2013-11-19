import os
import sys
import logging
from time import sleep

from AVMaster import vm_manager

def execute(vm, args):
    """ server side """
    clean = True # VM IS NOT INFECTED!! TEST CAN CONTINUE!!!

    logging.debug("    CS Execute")
    assert vm, "null vm"

    dirs = ['C:/Users/avtest/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup',
            'C:/Documents and Settings/avtest/Start Menu/Programs/Startup', 'C:/Users/avtest/Desktop']

    for d in dirs:
        out = vm_manager.execute(vm, "list_directory", d)
        print out
        if out is not None:
            clean = False

    if clean is True:
        return True, "VM is not infected"
    else:
        return False, "VM is INFECTED!!!!"
