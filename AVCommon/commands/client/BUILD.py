__author__ = 'fabrizio'


import logging
import time

from AVCommon import command
from AVAgent import build

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
    logging.debug("    BUILD %s" % args)
    assert vm, "null vm"
    assert command.context, "Null context"

    backend = command.context["backend"]
    frontend = command.context["frontend"]
    redis = command.context["redis"]

    action, platform, kind = args

    ret = build.build(action, platform, kind, backend, frontend)

    time.sleep(10)
    logging.debug("stop sleeping")
    return True, ret