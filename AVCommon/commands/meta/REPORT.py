__author__ = 'zeno'

from AVCommon.logger import logging
import time

from AVCommon import command
from AVCommon.procedure import Procedure

def execute(vm, protocol, mon_args):
    """ client side, returns (bool,*) """
    logging.debug("    SET %s" % str(mon_args))

    assert vm, "null vm"
    assert command.context is not None

    assert isinstance(mon_args, list), "VM expects a list"

    assert protocol
    assert protocol.procedure

    logging.debug("insert report init")

    command_list = []

    command_list.append("REPORT_INIT")
    for proc_token in mon_args:

        report_args = []
        if isinstance(proc_token, basestring):
            proc_name = proc_token
        elif isinstance(proc_token, dict):
            assert len(proc_token.keys()) == 1
            proc_name = proc_token.keys()[0]
            report_args = proc_token[proc_name]
        else:
            return False, "Error parsing"

        logging.debug("insert report kind: %s args: %s" % (proc_name, report_args))
        command_list.append(["REPORT_KIND_INIT", None, (proc_name)])
        command_list.append(["CALL", None, (proc_name)])
        command_list.append(["REPORT_KIND_END", None, (proc_name, report_args)])

    command_list.append("REPORT_END")

    proc = Procedure("_REPORT", command_list)
    protocol.procedure.insert(proc)

    #logging.debug("procedure: %s" % (protocol.procedure.command_list))
    #logging.debug("report items: %s" % (command.context))
    return True, "REPORT"