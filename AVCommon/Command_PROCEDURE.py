import logging

import command


class Command_PROCEDURE(command.ClientCommand):
    """ server side """

    def on_init(self, args):
        logging.debug("    CS on_init")

    def on_answer(self, success, answer):
        logging.debug("    CS on_answer")

    """ client side, returns (bool,*) """
    def execute(self, args):
        logging.debug("    CS Execute")
        return True, ""


