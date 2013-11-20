import os
import sys
import logging

def execute(vm, args):
    """ server side """
    from AVMaster import vm_manager

    logging.debug("    CS Execute")
    assert vm, "null vm"

    ret = vm_manager.execute(vm, "runTest", args)

    if ret == 0:
        return True, "Command %s executed" % args
    else:
        return False, "Command %s not executed" % args


