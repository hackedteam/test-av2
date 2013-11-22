__author__ = 'zeno'

import logging
import time

from AVCommon import command
from AVAgent import build


def on_init(protocol, args):
    pass


def on_answer(vm, success, answer):
    pass


def execute(vm, args):
    failed = build.check_static(args)

    return not failed, failed