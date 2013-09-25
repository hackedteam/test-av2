import Command
import logging
from Decorators import *

class Command_END(Command.ClientCommand):

    """ server side """
    def on_init(self, args):
        logging.debug("    CS on_init")
        pass

    def on_answer(self, success, answer):
        logging.debug("    CS on_answer")

    """ client side, returns (bool,*) """
    def execute(self, args):
        logging.debug("    CS Execute")
        return True, "It's time to die"


