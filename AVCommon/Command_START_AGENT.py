import logging

import command


class Command_START_AGENT(command.ClientCommand):
    """ starts a vmAgent on a vm and connects it to the mqstar """

    def on_init(self, args):
        """ server side """
        logging.debug("    CS on_init")

    def on_answer(self, success, answer):
        """ server side """
        logging.debug("    CS on_answer")


    def execute(self, args):
        """ client side, returns (bool,*) """
        logging.debug("    CS Execute")
        return True, ""


