import logging

import command


class Command_STOP_VM(command.ServerCommand):
    """ stops a vm """

    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute")
        return True, ""


