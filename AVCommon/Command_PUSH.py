import logging

import command


class Command_PUSH(command.ServerCommand):
    """ server side """

    def execute(self, args):
        logging.debug("    CS Execute")
        return True, ""


