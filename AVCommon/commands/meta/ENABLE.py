__author__ = 'zeno'

import datetime
from AVCommon.logger import logging

from AVCommon.procedure import Procedure

def execute(vm, protocol, args):
    logging.debug("    CS Execute: args %s" % args)

    assert protocol
    assert protocol.procedure

    if not args:
        protocol.on_error = "DISABLED"
        return True, "Procedure disabled"

    week   = ['sunday',
              'monday',
              'tuesday',
              'wednesday',
              'thursday',
              'friday',
              'saturday']

    today = datetime.datetime.today().weekday()
    today_week = week[today + 1]

    if isinstance(args, list):
        for d in args:
            assert d.lower() in week
        if not today_week in args:
            protocol.on_error = "DISABLED"
            return True, "Today not allowed"

    return True, args
