__author__ = 'fabrizio'

import logging
import time

from AVCommon import command

vm = None

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
    logging.debug("    GET %s" % args)

    assert vm, "null vm"
    assert command.context is not None

    key = args
    if key not in command.context:
        return False, "Key not found: %s" % command.context.keys()
    value = command.context[key]

    logging.debug("key: %s value: %s" % (key, value))
    return True, value