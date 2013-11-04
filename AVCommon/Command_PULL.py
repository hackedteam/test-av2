import logging

import command


#TODO
class Command_PULL(command.ServerCommand):
    """ Pulls a set of files from a vm """

    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"

        #TODO pull files from self.vm
        return True, ""
