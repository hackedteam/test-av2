__author__ = 'fabrizio'


import logging
import thread

import command

class Command_BUILD(command.ClientCommand):
    """ eval called client side. Use with care. """

    def execute(self, args):
        """ client side, returns (bool,*) """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"

        ret = "BUILD"
        thread.sleep(30)
        logging.debug("stop sleeping")
        return True, ret