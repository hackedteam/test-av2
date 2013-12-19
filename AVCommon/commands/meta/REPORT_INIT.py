__author__ = 'zeno'

from AVCommon import command
from AVCommon.logger import logging

def execute(vm, protocol, args):
    # counts the inits
    from AVMaster import report

    logging.debug("    CS REPORT_INIT:  %s,%s" % (vm,args))
    #if "report" not in command.context.keys():
    #    logging.info("report init: %s" % args)
    #    command.context["report"] = set()
        #report.init(args)

    #command.context["report"].add(vm)
    #assert command.context["report"]

    return True, vm
