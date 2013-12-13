__author__ = 'zeno'

from AVCommon.logger import logging
import time

from AVCommon import command
from AVCommon.procedure import Procedure

def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    SET %s" % str(args))

    assert vm, "null vm"
    assert command.context is not None

    protocol, mon_args = args

    assert isinstance(mon_args, list), "VM expects a list"

    assert protocol
    assert protocol.procedure

    logging.debug("insert report init")

    command_list = []

    command_list.append("REPORT_INIT")
    for proc_name in mon_args:
        logging.debug("insert report kind: %s" % (proc_name))
        command_list.append(["REPORT_KIND", None, (proc_name)])
        command_list.append(["CALL", None, (proc_name)])

    command_list.append("REPORT_END")

    proc = Procedure("_REPORT", command_list)
    protocol.procedure.insert(proc)

    #logging.debug("procedure: %s" % (protocol.procedure.command_list))
    #logging.debug("report items: %s" % (command.context))
    return True, "REPORT"