import logging

import command


class Command_START_AGENT(command.ServerCommand):
    """ server side """

    def execute(self, args):
        logging.debug("    CS Execute")
        return True, ""


