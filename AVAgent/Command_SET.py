__author__ = 'fabrizio'

import logging
import time

import command

class Command_SET(command.ClientCommand):
    """ eval called client side. Use with care. """

    def execute(self, args):
        """ client side, returns (bool,*) """
        logging.debug("    SET %s" % args)

        assert self.vm, "null self.vm"
        assert command.context is not None

        key, value = args.split("=", 1)
        command.context[key] = value

        logging.debug("key: %s value: %s" % (key, value))
        return True, key

