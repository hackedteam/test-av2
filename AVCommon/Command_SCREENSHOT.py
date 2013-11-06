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

    def execute(self, img_path):
        """ server side """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"
        #img_path = "/tmp/img_path.png"

        #TODO get screenshot from self.vm
        try:
            VMManager.execute(self.vm, "takeScreenshot", img_path)
            return True, "Screenshot saved on file %s" % img_path
        except Exception as e:
        	return False, "Screenshot not saved. Error Occurred: %s" % e

