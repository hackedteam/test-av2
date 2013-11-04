import logging

import command


class Command_EVAL_SERVER(command.ServerCommand):
    """ eval called server side. Use with care. """

    def execute(self, args):
<<<<<<< HEAD
        #logging.debug("    CS Execute: %s" % args)
=======
        """ client side, returns (bool,*) """
        logging.debug("    CS Execute: %s" % args)
>>>>>>> 4ec4fc7261196ee02f081437685658a762360a1f
        ret = eval(args)
        #logging.debug("    CS Execute ret: %s" % ret)
        return True, ret


