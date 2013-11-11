import logging

import command
from AVMaster import vm_manager

#noinspection PyPep8Naming
class Command_START_AGENT(command.ClientCommand):
    """ starts a vmAgent on a vm and connects it to the mqstar """

    def on_init(self, args):
        """ server side """
        logging.debug("    CS on_init")

        #TODO: push files on client
        assert self.vm, "null self.vm"

    def on_answer(self, success, answer):
        """ server side """
        logging.debug("    CS on_answer")
        assert self.vm, "null self.vm"


    def execute(self, args):
        """ client side, returns (bool,*) """
        logging.debug("    START AGENT")
        assert self.vm, "null self.vm"

        return True, "AGENT STARTED"


