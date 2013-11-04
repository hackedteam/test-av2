import logging

import command

class Command_COMMAND_CLIENT(command.ClientCommand):
    """ executes a command on a client. The command can be implemented only client side. """
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

        #TODO execute args on self.vm
        return True, ""

