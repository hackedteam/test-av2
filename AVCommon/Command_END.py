import logging

import command


class Command_END(command.ServerCommand):
    """ ends a protocol communication """
    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute")
        return True, "It's time to die"


