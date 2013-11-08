import os
import sys
import logging
from time import sleep

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import command
from AVMaster import vm_manager

#noinspection PyPep8Naming
class Command_STOP_VM(command.ServerCommand):
    """ stops a vm """

    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"

        ret = vm_manager.execute(self.vm, "shutdown")
        if ret:
            for i in range(0,6):
                if vm_manager.execute(self.vm, "is_powered_off"):
                    return True, "Stopped VM"
                sleep(10)
            return False, "Error Occurred: Timeout while stopping VM"
        else:
            return False, "Not Stopped VM"
