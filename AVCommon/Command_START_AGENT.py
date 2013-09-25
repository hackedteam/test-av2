import Command
import logging

class Command_START_AGENT(Command.ServerCommand):

    """ server side """
    def execute(self, args):
        logging.debug("    CS Execute")
        return True, ""


