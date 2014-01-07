__author__ = 'zeno'

from AVCommon.logger import logging
from AVCommon import command

def execute(vm, protocol, args):
    # change the kind for the vm
    from AVMaster import report

    logging.debug("    CS REPORT_KIND:  %s,%s" % (vm,args))
    #assert vm in command.context["report"], "report: %s" % command.context["report"]
    protocol.error = False

    report.set_procedure(vm, args)
    return True, "%s| %s" % (vm, args)
