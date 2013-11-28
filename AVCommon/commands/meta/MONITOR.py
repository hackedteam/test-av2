__author__ = 'zeno'

import logging
import time

from AVCommon import command

def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    SET %s" % str(args))

    assert vm, "null vm"
    assert command.context is not None

    protocol, mon_args = args

    assert isinstance(mon_args, list), "VM expects a list"

    dispatch = protocol.dispatcher

    logging.debug("items: %s" % (command.context))
    return True, "MONITOR"