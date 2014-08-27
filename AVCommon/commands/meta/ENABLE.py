__author__ = 'zeno'

import datetime
from AVCommon.logger import logging

from AVCommon.procedure import Procedure

def execute(vm, protocol, args):
    logging.debug("    CS Execute: args %s" % args)

    assert protocol
    assert protocol.procedure

    protocol.on_error = "SKIP"

    if not args:
        return False, "Procedure disabled"

    week   = ['sunday',
              'monday',
              'tuesday',
              'wednesday',
              'thursday',
              'friday',
              'saturday']

    today = datetime.datetime.today().weekday()
    today_week = week[today]

    if isinstance(args, list):
        for d in args:
            assert d.lower() in week
        if not today_week in args:
            return False, "Today not allowed"

    return True, args
