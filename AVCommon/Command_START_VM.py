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
        try:
            vm_manager.execute(self.vm, "startup")
            while vm_manager.execute(self.vm, "is_powered_on") is False:
#                logging.debug("sleeping 5 secs waiting for startup")
                sleep(3)            
            return True, "Started VM"
        except Exception as e:
            return False, "Error Occurred: %s" % e
