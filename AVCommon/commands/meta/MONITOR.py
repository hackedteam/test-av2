__author__ = 'zeno'

import logging
import time

from AVCommon import command

def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    SET %s" % str(args))

    assert vm, "null vm"
    assert command.context is not None

    assert isinstance(args, list), "VM expects a list"

    command.context["VM"] = args

    logging.debug("items: %s" % (command.context))
    return True, "VM"