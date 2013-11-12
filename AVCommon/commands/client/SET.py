__author__ = 'fabrizio'

import logging
import time

from AVCommon import command

def on_init(vm, args):
    """ server side """
    logging.debug("    CS on_init")

    #TODO: push files on client
    assert vm, "null vm"

def on_answer(vm, success, answer):
    """ server side """
    logging.debug("    CS on_answer")
    assert vm, "null vm"


def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    SET %s" % str(args))

    assert vm, "null vm"
    assert command.context is not None

    assert isinstance(args, list), "SET expects a list"

    for arg in args:
        key, value = arg #.split("=", 1)
        command.context[key.strip()] = value.strip()

    logging.debug("items: %s" % (command.context))
    return True, key

