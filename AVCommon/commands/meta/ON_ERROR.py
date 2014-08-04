__author__ = 'fabrizio'


from AVCommon.logger import logging
from AVCommon import config
import time

from AVCommon import command

def execute(vm, protocol, args):

    assert isinstance(args, str)
    value = args.upper()

    assert value in ["SKIP", "CONTINUE", "STOP"]
    protocol.on_error = value

    return True, "on_error: %s" % args
