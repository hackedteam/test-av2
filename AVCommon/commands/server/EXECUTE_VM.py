import os
import sys
import logging

def execute(vm, args):
    """ server side """
    from AVMaster import vm_manager

    logging.debug("    CS Execute")
    assert vm, "null vm"

    if isinstance(args, list):
        cmd_args = tuple(args)
    else:
        cmd_args = (args,)
    ret = vm_manager.execute(vm, "executeCmd", *cmd_args)

    if ret == 0:
        return True, "Command %s executed" % args
    else:
        return False, "Command %s not executed" % args


