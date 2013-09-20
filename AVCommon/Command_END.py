import Command
import logging
from Decorators import *

class Command_END(Command.ClientCommand):

    """ server side """
    def onInit(self, args):
        logging.debug("    CS onInit")
        pass

    def onAnswer(self, success, answer):
        logging.debug("    CS onAnswer")

    """ client side, returns (bool,*) """
    def Execute(self, args):
        logging.debug("    CS Execute")
        return True, "It's time to die"


