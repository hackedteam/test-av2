import Command
import logging

class Command_EVAL_CLIENT(Command.ClientCommand):

    """ server side """
    def onInit(self, args):
        logging.debug("    CS onInit")

    def onAnswer(self, success, answer):
        logging.debug("    CS onAnswer")

    """ client side, returns (bool,*) """
    def Execute(self, args):
        logging.debug("    CS Execute")
        ret = eval(args)
        return True, ret


