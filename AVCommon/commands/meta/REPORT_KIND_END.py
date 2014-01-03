__author__ = 'zeno'

from AVCommon.logger import logging
from AVCommon import command

def execute(vm, protocol, args):
    # change the kind for the vm
    from AVMaster import report

    logging.debug("    CS REPORT_KIND_END:  %s,%s" % (vm,args))
    #assert vm in command.context["report"], "report: %s" % command.context["report"]

    success = not protocol.error
    logging.debug("%s, success: %s" % (vm, success))

    return success, "%s| %s" % (vm, args)
