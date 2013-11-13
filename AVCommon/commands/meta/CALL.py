import logging

from AVCommon.procedure import Procedure

def execute(vm, args):
    logging.debug("    CS Execute")
    protocol, proc_name = args

    proc = Procedure.procedures[proc_name]
    protocol.procedure.insert(proc)

    return True, ""
