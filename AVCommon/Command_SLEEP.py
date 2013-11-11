import logging
from time import sleep

import command

class Command_SLEEP(command.ServerCommand):

    """ server side """
    def execute(self, args):
        assert isinstance(args, int) and len(args) == 1, "Sleep needs only an int as argument"
        logging.debug("    CS Sleep for %s" % args)
        sleep(args)
        return True, "sleeped for %s" % args


