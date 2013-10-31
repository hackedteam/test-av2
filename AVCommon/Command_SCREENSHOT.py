import logging

import command


class Command_SCREENSHOT(command.ServerCommand):
    """ gets a screenshot from a vm """

    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute")
        return True, ""


