__author__ = 'fabrizio'

import logging
import time

from AVCommon import command




class Command_SET(command.ClientCommand):
    """ eval called client side. Use with care.
    Example:

    SET:
        - [foo,bar]
        - [key,value]

    """

    def execute(self, args):
        """ client side, returns (bool,*) """
        logging.debug("    SET %s" % str(args))

        assert self.vm, "null self.vm"
        assert command.context is not None

        assert isinstance(args, list), "SET expects a list"

        for arg in args:
            key, value = arg #.split("=", 1)
            command.context[key.strip()] = value.strip()

        logging.debug("items: %s" % (command.context))
        return True, key

