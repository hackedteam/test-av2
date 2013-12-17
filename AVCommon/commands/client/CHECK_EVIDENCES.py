__author__ = 'fabrizio'

from AVCommon.logger import logging
from AVCommon import command


def on_init(protocol, args):
    return True


def on_answer(vm, success, answer):
    pass


def execute(vm, args):
    from AVAgent import build

    type_ev = args.pop(0)
    key, value = None, None
    if args:
        key, value = args


    backend = command.context["backend"]
    try:
        success, ret = build.check_evidence(backend, type_ev, key, value)
        return success, ret
    except:
        logging.exception("%s, Cannot check evidences" % vm)
        return False, "Error checking evidences"
