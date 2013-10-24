import logging

import command


class Command_REVERT(command.ServerCommand):
    """ server side """

    def execute(self, args):
        logging.debug("    CS Execute")
        return True, ""


