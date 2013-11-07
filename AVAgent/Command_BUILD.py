__author__ = 'fabrizio'


import logging
import time

import command

class Command_BUILD(command.ClientCommand):
    """ eval called client side. Use with care. """

    def execute(self, args):
        """ client side, returns (bool,*) """
        logging.debug("    BUILD %s" % args)
        assert self.vm, "null self.vm"

        # parametri da passare:
        # backend, frontend, redis
        # platform, kind
        # params (

        ret = "BUILT in 10 sec"
        time.sleep(10)
        logging.debug("stop sleeping")
        return True, ret