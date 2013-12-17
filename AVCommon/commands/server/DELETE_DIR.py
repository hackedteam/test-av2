import os
import sys
from AVCommon.logger import logging


def execute(vm, args):
    from AVMaster import vm_manager

    #logging.debug("    CS Execute")
    assert vm, "null vm"
    #assert len(args) == 1 and isinstance(args, str), "Argument must be a string."
    assert isinstance(args, str), "Argument must be single."

    dirname = args.replace('/','\\')
    logging.debug("Deleting %s from %s" % (dirname, vm))
    r = vm_manager.execute(vm, "deleteDirectoryInGuest", dirname)

    return True, "%s deleted" % dirname

    # TODO: return True only if directory is deleted for real

    """
    if r == 0:
        return True, "Deleted %s" % args
    else:
        return False, "Not deleted %s" % args
    """