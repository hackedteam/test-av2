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

       	ret = vm_manager.execute(self.vm, "runTest", args)

        if ret == 0:
            return True, "Command %s executed" % args
        else:
            return False, "Command %s not executed" % args


