import logging

import command
from procedure import Procedure

class Command_COMMAND_CLIENT(command.ClientCommand):

    client_commands = None

    """ executes a command on a client. The command can be implemented only client side. """
    def on_init(self, args):
        """ server side """
        logging.debug("    CS on_init")

    def on_answer(self, success, answer):
        """ server side """
        logging.debug("    CS on_answer")

    def execute(self, args):
        """ client side, returns (bool,*) """

        assert self.vm, "null self.vm"

        procedure = Procedure(args)
        logging.debug("    CS Execute procedure %s" % procedure)
        ret = []
        while True:
            if not procedure:
                break
            c = procedure.next_command()
            logging.debug("        next command: %s" % c)
            ret.append(c.execute())

        logging.debug("    CS res: %s" % ret)
        return True, ret


