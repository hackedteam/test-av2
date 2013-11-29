__author__ = 'zeno'

from AVMaster import report
from AVCommon import command
import logging

def execute(vm, args):
    # counts the inits
    protocol, args = args
    logging.debug("    CS Execute: %s" % args)
    if "report" not in command.context.keys():
        logging.info("report init: %s" % args)
        #command.context["report"] = set()
        #report.init(args)

    #command.context["report"].add(vm)


    return True, ""
