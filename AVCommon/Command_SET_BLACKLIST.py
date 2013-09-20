import Command
import logging

class Command_SET_BLACKLIST(Command.ClientCommand):

    """ server side """
    def onInit(self, args):
        logging.debug("    CS onInit")

    def onAnswer(self, success, answer):
        logging.debug("    CS onAnswer")

    """ client side, returns (bool,*) """
    def Execute(self, args):
        logging.debug("    CS Execute")
        return True, ""


