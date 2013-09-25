import Command
import logging

class Command_STOPVM(Command.ServerCommand):

    """ server side """
    def execute(self, args):
        logging.debug("    CS Execute")
        return True, ""


