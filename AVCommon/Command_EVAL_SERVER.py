import Command
import logging

class Command_EVAL_SERVER(Command.ServerCommand):

    """ client side, returns (bool,*) """
    def execute(self, args):
        logging.debug("    CS Execute")
        ret = eval(args)
        return True, ret


