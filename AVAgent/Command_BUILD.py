__author__ = 'fabrizio'


import logging
import time

from AVCommon import command
import build

class Command_BUILD(command.ClientCommand):
    """ eval called client side. Use with care. """

    def execute(self, args):
        """ client side, returns (bool,*) """
        logging.debug("    BUILD %s" % args)
        assert self.vm, "null self.vm"
        assert command.context, "Null context"

        backend = command.context["backend"]
        frontend = command.context["frontend"]
        redis = command.context["redis"]

        action, platform, kind = args

        ret = build.build(action, platform, kind, backend, frontend)

        time.sleep(10)
        logging.debug("stop sleeping")
        return True, ret