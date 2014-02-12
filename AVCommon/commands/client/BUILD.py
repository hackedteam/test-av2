__author__ = 'fabrizio'

from AVCommon.logger import logging
import time
import socket

from AVCommon import command
from AVAgent import build

report_level = 1


def on_init(protocol, args):
    """ server side """
    args.append(socket.gethostname())
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
    params = command.context["build_parameters"].copy()
    blacklist = command.context["blacklist"][:]
    soldierlist = command.context["soldierlist"][:]
    nointernetcheck = command.context["nointernetcheck"][:]
    operation = command.context["operation"]

    report = command.context["report"]

    logging.debug("args: %s", args)
    action, platform, kind, operation = args

    param = params[platform]
    platform_type = param['platform_type']

    assert kind in ['silent', 'melt'], "kind: %s" % kind
    assert action in ['scout', 'elite', 'elite_fast', 'soldier_fast', 'internet', 'test', 'clean', 'pull'], "action: %s" % action
    assert platform_type in ['desktop', 'mobile'], "platform_type: %s" % platform_type

    results, success, errors = build.build(action, platform, platform_type, kind, param, operation, backend, frontend, blacklist, soldierlist, nointernetcheck, report)

    try:
        last_result = results[-1]
    except:
        last_result = "NO RESULTS"

    return success, results


