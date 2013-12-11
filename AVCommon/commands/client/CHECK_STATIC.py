__author__ = 'zeno'

from AVCommon.logger import logging
import time
import glob

from AVCommon import command
from AVAgent import build


def on_init(protocol, args):
    pass


def on_answer(vm, success, answer):
    pass


def execute(vm, args):
    files = glob.glob(args)
    logging.debug("Expanded files: %s" % files)
    failed = build.check_static(files, command.context["report"])

    return failed==[], failed