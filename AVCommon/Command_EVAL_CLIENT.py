import logging

import command


#noinspection PyPep8Naming
class Command_EVAL_CLIENT(command.ClientCommand):
    """ eval called client side. Use with care. """

    def on_init(self, args):
        """ server side """
        logging.debug("    CS on_init")

    def on_answer(self, success, answer):
        """ server side """
        logging.debug("    CS on_answer")

    def execute(self, args):
        """ client side, returns (bool,*) """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"

        ret = eval(args)
        return True, ret


