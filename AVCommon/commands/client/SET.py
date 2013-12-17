__author__ = 'fabrizio'

from AVCommon.logger import logging
import time

from AVCommon import command
from AVCommon import config


def on_init(protocol, args):
    """ client side, returns (bool,*) """

    logging.debug("    SET %s" % str(args))
    assert command.context is not None
    assert isinstance(args, dict), "SET expects a dict"

    for k, v in args.items():
        command.context[k] = v

    if config.verbose:
        logging.debug("items: %s" % (command.context))
    return True


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

