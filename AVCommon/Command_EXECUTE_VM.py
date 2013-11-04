import logging

import command


class Command_EXECUTE_VM(command.ServerCommand):
    """ Executes a program on a vm """

    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute")
        return True, ""


