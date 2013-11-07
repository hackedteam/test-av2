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

        #TODO: shutsdown self.vm
        try:
            vm_manager.execute(self.vm, "shutdown")
            while vm_manager.execute(self.vm, "is_powered_off") is False:
#                logging.debug("sleeping 5 secs waiting for startup")
                sleep(3)
            return True, "Stopped VM"
        except Exception as e:
            return False, "Error Occurred: %s" % e
