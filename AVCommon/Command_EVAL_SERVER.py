import logging

import command


class Command_EVAL_SERVER(command.ServerCommand):
    """ eval called server side. Use with care. """

    def execute(self, args):
        """ client side, returns (bool,*) """
        logging.debug("    CS Execute: %s" % args)
        assert self.vm, "null self.vm"

        ret = eval(args)
        #logging.debug("    CS Execute ret: %s" % ret)
        return True, ret


