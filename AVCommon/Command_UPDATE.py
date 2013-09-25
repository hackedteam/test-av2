import Command
import logging

class Command_UPDATE(Command.ServerCommand):

    """ server side """
    def execute(self, args):
        logging.debug("    CS Execute")
        return True, ""


