import logging

import command

#TODO
class Command_SCREENSHOT(command.ServerCommand):
    """ gets a screenshot from a vm """

    def execute(self, vm):
        """ server side """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"

        #TODO get screenshot from self.vm
        return True, ""


