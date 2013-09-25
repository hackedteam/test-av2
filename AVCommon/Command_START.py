import Command
import logging


class Command_START(Command.ClientCommand):

    """ server side """
    def on_init(self, args):
        logging.debug("    CS on_init")
        pass

    def on_answer(self, success, answer):
        logging.debug("    CS on_answer")

    """ client side, returns (bool,*)"""
    def execute(self, args):
        logging.debug("    CS Execute")
        return True, "I'm doing Science and I'm alive"
