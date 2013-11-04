import logging

import command

#TODO
class Command_EXECUTE_VM(command.ServerCommand):
    """ Executes a program on a vm """

    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"

        #TODO execute program on self.vm
        return True, ""


