from AVCommon.logger import logging
from AVCommon.procedure import Procedure
import command

def execute(vm, protocol, proc_name):
    logging.debug("    CS Execute: %s" % proc_name)

    proc = Procedure.procedures[proc_name]

    assert protocol
    assert protocol.procedure

    proc.append_command(["END_CALL", None, proc_name])
    protocol.procedure.insert(proc)

    return True, proc_name
