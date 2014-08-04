__author__ = 'zeno'
from AVCommon.logger import logging
from AVCommon import command

def execute(vm, protocol, args):
    """ client side, returns (bool,*) """
    logging.debug("    SET %s" % str(args))

    assert vm, "null vm"
    assert command.context is not None

    assert isinstance(args, dict), "SET expects a dict"

    for k, v in args.items():
        command.context[k] = v

    logging.debug("items: %s" % (command.context))
    return True, k