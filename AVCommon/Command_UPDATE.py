import logging

import command


class Command_UPDATE(command.ServerCommand):
    """ updates a vm """

    def execute(self, args):
        logging.debug("    CS Execute")
        return True, ""


