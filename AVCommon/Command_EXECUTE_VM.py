import os
import sys
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import command
from AVMaster import vm_manager

#TODO
class Command_EXECUTE_VM(command.ServerCommand):
    """ Executes a program on a vm """

    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"

        #TODO execute program on self.vm
        try:
        	ret = vm_manager.execute(self.vm, "runTest", args)
        	return True, ret
        except Exception as e:
        	return False, "Error Occurred: %s" % e


