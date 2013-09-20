import Command
import logging

class Command_PUSH(Command.ServerCommand):

    """ server side """
    def Execute(self, args):
        logging.debug("    CS Execute")
        return True, ""


