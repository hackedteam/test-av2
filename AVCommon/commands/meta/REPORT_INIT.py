__author__ = 'zeno'

from AVCommon import command
import logging

def execute(vm, args):
    # counts the inits
    from AVMaster import report

    protocol, args = args
    logging.debug("    CS REPORT_INIT:  %s,%s" % (vm,args))
    if "report" not in command.context.keys():
        logging.info("report init: %s" % args)
        command.context["report"] = set()
        #report.init(args)

    command.context["report"].add(vm)
    assert command.context["report"]

    return True, vm
