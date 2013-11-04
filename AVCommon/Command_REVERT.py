import os
import sys
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVCommon.command import Command
from AVMaster.vm_manager import VMManager

class Command_REVERT(command.ServerCommand):
    """ reverts a vm """

    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute REVERT")
        VMManager.execute(Command.context.vm_name, self.cmd)
        return True, ""


