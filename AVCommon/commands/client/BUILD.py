__author__ = 'fabrizio'

from AVCommon.logger import logging
import time

from AVCommon import command
from AVAgent import build

report_level = 1


def on_init(protocol, args):
    """ server side """
    return True


def on_answer(vm, success, answer):
    """ server side """
    if isinstance(answer, list) and len(answer) > 0:
        logging.info("BUILD ANSWER LAST: %s" % answer[-1])
    else:
        logging.info("BUILD ANSWER: %s" % str(answer))


def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    BUILD %s" % args)
    assert vm, "null vm"
    assert command.context, "Null context"

    backend = command.context["backend"]
    frontend = command.context["frontend"]
    params = command.context["build_parameters"]
    blacklist = command.context["blacklist"]

    report = command.context["report"]

    logging.debug("args: %s", args)
    action, platform, kind = args

    param = params[platform]
    platform_type = param['platform_type']

    assert kind in ['silent', 'melt'], "kind: %s" % kind
    assert action in ['scout', 'elite', 'internet', 'test', 'clean', 'pull'], "action: %s" % action
    assert platform_type in ['desktop', 'mobile'], "platform_type: %s" % platform_type

    ret = build.build(action, platform, platform_type, kind, param, backend, frontend, blacklist, report)

    time.sleep(10)
    logging.debug("stop sleeping")
    return True, ret


