import logging

import command


class Command_PUSH(command.ServerCommand):
    """ Pulls a set of files from a vm """
    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute")
        return True, ""


