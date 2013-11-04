import logging

import command


class Command_START_AGENT(command.ClientCommand):
    """ starts a vmAgent on a vm and connects it to the mqstar """

    def on_init(self, args):
        """ server side """
        logging.debug("    CS on_init")
        assert self.vm, "null self.vm"

    def on_answer(self, success, answer):
        """ server side """
        logging.debug("    CS on_answer")
        assert self.vm, "null self.vm"


    def execute(self, args):
        """ client side, returns (bool,*) """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"

        #TODO: start a AVAgent on a vm, possibly all files are already pushed
        return True, ""


