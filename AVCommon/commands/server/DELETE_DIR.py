import os
import sys
import logging


def execute(vm, args):
    from AVMaster import vm_manager

    logging.debug("    CS Execute")
    assert vm, "null vm"
    #assert len(args) == 1 and isinstance(args, str), "Argument must be a string."
    assert isinstance(args, str), "Argument must be single."

    logging.debug("Deleting %s from %s" % (args, vm))
    r = vm_manager.execute(vm, "deleteDirectoryInGuest", args)

    return True, "%s deleted" % args

    # TODO: return True only if directory is deleted for real

    """
    if r == 0:
        return True, "Deleted %s" % args
    else:
        return False, "Not deleted %s" % args
    """