__author__ = 'zeno'
import logging

import command


#noinspection PyPep8Naming
class Command_STOP_AGENT(command.ClientCommand):
    """ stops a vmAgent on a vm """

    def on_init(self, args):
        """ server side """
        logging.debug("    CS on_init")

    def on_answer(self, success, answer):
        """ server side """
        logging.debug("    CS on_answer")

    def execute(self, args):
        """ client side, returns (bool,*) """
        logging.debug("    STOP_AGENT")
        assert self.vm, "null self.vm"

        #TODO: stops a AVAgent on self.vm
        return True, ""