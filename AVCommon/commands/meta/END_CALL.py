__author__ = 'zeno'

import datetime
from AVCommon.logger import logging


def execute(vm, protocol, args):
    logging.debug("    CS Execute: args %s" % args)
    protocol.on_error = "SKIP"
    return True, args