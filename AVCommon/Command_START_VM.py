import logging

import command


class Command_START_VM(command.ServerCommand):
    """ server side """

    def execute(self, args):
        logging.debug("    CS Execute")
        return True, "I'm doing Science and I'm alive"
