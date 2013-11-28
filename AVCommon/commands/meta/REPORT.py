__author__ = 'zeno'

import logging
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

    report = protocol.dispatcher.report



    assert protocol
    assert protocol.procedure
    protocol.procedure.insert(proc)

    for proc_name in mon_args:
        protocol.procedure.insert(REPORT_INIT)
        proc = Procedure.procedures[proc_name]
        protocol.procedure.insert(proc)
        protocol.procedure.insert(REPORT_COLLECT)
        columns[c] = report.results

    protocol.procedure.insert(REPORT_END)


    logging.debug("items: %s" % (command.context))
    return True, "MONITOR"