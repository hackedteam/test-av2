__author__ = 'fabrizio'

import os
import logging
from AVCommon import command

def on_init(protocol, args):
    pass


def on_answer(vm, success, answer):
    pass


def execute(vm, args):
    from AVAgent import build
    logging.debug("    CS CHECK_EMPTY_DIR:  %s,%s" % (vm,args))

    assert isinstance(args, basestring)

    if not os.path.exists(args):
        res = True, "Not existent dir: %s" % args
    else:
        l = os.listdir(args)
        if not l:
            res = True, "Empty dir: %s" % args
        else:
            res = False, "Non empty dir: %s" % l

    return res