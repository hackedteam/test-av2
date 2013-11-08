import os
import sys
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import command
from AVMaster import vm_manager

#TODO
class Command_PUSH(command.ServerCommand):
    """ Pulls a set of files from a vm """
    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"

        #TODO: push files to self.vm
        vm_manager.execute(self.vm, "copyFileToGuest", args)
        return True, ""
