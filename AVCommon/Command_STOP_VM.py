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
        tick = 0
        try:
            ret = vm_manager.execute(self.vm, "shutdown")
            while not vm_manager.execute(self.vm, "is_powered_off"):
#                logging.debug("sleeping 5 secs waiting for startup")
                if tick > 6:
                    raise Exception("Timeout while powering off VM")
                tick+=1
                sleep(10)
            if ret:
                return True, "Stopped VM"
            else:
                raise Exception("can't stop VM or VM already stopped")
        except Exception as e:
            return False, "Error Occurred: %s" % e
