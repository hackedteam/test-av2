__author__ = 'zeno'

from AVMaster import report
import logging

def execute(vm, args):
    # change the kind for the vm
    protocol, args = args
    logging.debug("    CS Execute: %s" % args)
    report.set_procedure(vm, args)
    return True, "%s: %s" % (vm, args)
