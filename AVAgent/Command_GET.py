__author__ = 'fabrizio'

import logging
import time

import command

class Command_GET(command.ClientCommand):
    """ eval called client side. Use with care. """

    def execute(self, args):
        """ client side, returns (bool,*) """
        logging.debug("    GET %s" % args)

        assert self.vm, "null self.vm"
        assert command.context is not None

        key = args
        if key not in command.context:
            return False, "Key not found: %s" % command.context.keys()
        value = command.context[key]

        logging.debug("key: %s value: %s" % (key, value))
        return True, value