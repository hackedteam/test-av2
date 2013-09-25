import Command
import logging

class Command_STARTVM(Command.ServerCommand):

    """ server side """
    def execute(self, args):
        logging.debug("    CS Execute")
        return True, "I'm doing Science and I'm alive"
