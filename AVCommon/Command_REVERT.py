import Command
import logging

class Command_REVERT(Command.ServerCommand):

    """ server side """
    def Execute(self, args):
        logging.debug("    CS Execute")
        return True, ""


