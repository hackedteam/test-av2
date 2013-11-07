import os
import sys
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import command
from AVMaster.vm_manager import VMManager

#noinspection PyPep8Naming
class Command_REVERT(command.ServerCommand):
    """ reverts a vm """

    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute REVERT")
        assert self.vm, "null self.vm"

        # TODO: check
        VMManager.execute(self.vm, "revert_to_snapshot")
        return True, "Reverted VM"


