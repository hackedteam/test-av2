__author__ = 'fabrizio'

import logging
import time

import command

class Command_BUILD(command.ClientCommand):
    """ eval called client side. Use with care. """

    def execute(self, args):
        """ client side, returns (bool,*) """
        logging.debug("    SET %s" % args)

        assert self.vm, "null self.vm"
        assert command.context not None

        key, value = args
        command.context[key] = value

        logging.debug("stop sleeping")
        return True, key

