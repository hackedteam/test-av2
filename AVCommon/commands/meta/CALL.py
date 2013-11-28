import logging

from AVCommon.procedure import Procedure

def execute(vm, args):
    protocol, proc_name = args
    logging.debug("    CS Execute: %s" % proc_name)

    proc = Procedure.procedures[proc_name]

    assert protocol
    assert protocol.procedure
    protocol.procedure.insert(proc)

    return True, proc_name
