import logging

import command


class Command_START_VM(command.ServerCommand):
    """ starts a vm """

    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute")
        return True, "I'm doing Science and I'm alive"
