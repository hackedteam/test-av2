__author__ = 'fabrizio'

import logging
import time

from AVCommon import command


def on_init(protocol, args):
    """ server side """
    pass


def on_answer(vm, success, answer):
    """ server side """
    pass


def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    SET %s" % str(args))

    assert vm, "null vm"
    assert command.context is not None

    assert isinstance(args, dict), "SET expects a dict"

    for k, v in args.items():
        command.context[k] = v

    logging.debug("items: %s" % (command.context))
    return True, k

