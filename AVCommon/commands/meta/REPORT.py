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


    assert protocol
    assert protocol.procedure
    protocol.procedure.insert(proc)

    protocol.procedure.insert("REPORT_INIT")
    for proc_name in mon_args:
        protocol.procedure.insert({"REPORT_KIND", None, proc_name})
        proc = Procedure.procedures[proc_name]
        protocol.procedure.insert(proc)

        #columns[c] = report.results

    protocol.procedure.insert("REPORT_END")


    logging.debug("items: %s" % (command.context))
    return True, "MONITOR"