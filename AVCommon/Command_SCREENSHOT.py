import os
import sys
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import command
from AVMaster import vm_manager

#noinspection PyPep8Naming
class Command_SCREENSHOT(command.ServerCommand):
    """ gets a screenshot from a vm """

    def execute(self, img_path):
        """ server side """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"
        #img_path = "/tmp/img_path.png"

        ret = vm_manager.execute(self.vm, "takeScreenshot", img_path)
        if ret is True:
            return ret, "Screenshot saved on file %s" % img_path
        else:
            return ret, "Screenshot not saved"

