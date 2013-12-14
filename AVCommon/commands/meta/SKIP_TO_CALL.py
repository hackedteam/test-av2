__author__ = 'fabrizio'


from AVCommon.logger import logging
from AVCommon import config
import time

from AVCommon import command

def execute(vm, args):

    protocol, args = args
    assert isinstance(args, bool)

    config.skip_to_call = args

    return True, "skip_to_call: %s" % args
