import logging

import command


class Command_EVAL_SERVER(command.ServerCommand):
    """ client side, returns (bool,*) """

    def execute(self, args):
        logging.debug("    CS Execute: %s" % args)
        ret = eval(args)
        logging.debug("    CS Execute ret: %s" % ret)
        return True, ret


