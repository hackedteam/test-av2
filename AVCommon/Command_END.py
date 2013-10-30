import logging

import command


class Command_END(command.ServerCommand):
    """ server side """
    def execute(self, args):
        logging.debug("    CS Execute")
        return True, "It's time to die"


