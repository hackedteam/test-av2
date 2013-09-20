import Command
import logging


class Command_STARTVM(Command.ServerCommand):

    """ server side """
    def onInit(self, args):
        logging.debug("    CS onInit")
        pass

    def onAnswer(self, success, answer):
        logging.debug("    CS onAnswer")

    """ client side, returns (bool,*) """
    def Execute(self, args):
        logging.debug("    CS Execute")
        return True, "I'm doing Science and I'm alive"
