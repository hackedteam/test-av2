import os
import sys
import logging
from time import sleep

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import command
from AVMaster import vm_manager

#noinspection PyPep8Naming
class Command_START_VM(command.ServerCommand):
    """ starts a vm """

    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"

        #TODO: start a VM: self.vm
        tick = 0
        try:
            ret = vm_manager.execute(self.vm, "startup")
            while not vm_manager.execute(self.vm, "is_powered_on"):
#                logging.debug("sleeping 5 secs waiting for startup")
                if tick > 6:
                    raise Exception("Timeout while starting VM")
                tick+=1
                sleep(10)
            if ret:
                return True, "Started VM"
            else:
                raise Exception("Not Started or Already Started")
        except Exception as e:
            return False, "Error Occurred: %s" % e
