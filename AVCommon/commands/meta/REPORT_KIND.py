__author__ = 'zeno'

import logging
from AVCommon import command

def execute(vm, args):
    # change the kind for the vm
    from AVMaster import report

    protocol, args = args
    logging.debug("    CS REPORT_KIND:  %s,%s" % (vm,args))
    #assert vm in command.context["report"], "report: %s" % command.context["report"]

    report.set_procedure(vm, args)
    return True, "%s| %s" % (vm, args)
