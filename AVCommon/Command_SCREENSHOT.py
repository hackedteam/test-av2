import os
import sys
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import command
from AVMaster.vm_manager import VMManager

#TODO
class Command_SCREENSHOT(command.ServerCommand):
    """ gets a screenshot from a vm """

    def execute(self, vm):
        """ server side """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"

        #TODO get screenshot from self.vm
        VMManager.execute(self.vm, "takeScreenshot")
        return True, ""


