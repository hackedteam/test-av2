import Command
import logging

class Command_START(Command.Command):

    """ server side """
    def onInit(self):
        logging.debug("    CS onInit")
        pass

    def onAnswer(self, success, answer):
        logging.debug("    CS onAnswer")

    """ client side """
    def Execute(self):
        logging.debug("    CS Execute")
        return True, "I'm doing Science and I'm alive"


