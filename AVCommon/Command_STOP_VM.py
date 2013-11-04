import os
import sys
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import command
from AVMaster.vm_manager import VMManager

class Command_STOP_VM(command.ServerCommand):
    """ stops a vm """

    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"

        #TODO: shutsdown self.vm
<<<<<<< HEAD
        VMManager.execute(self.vm, "shutdown")
        return True, ""
=======
        return True, "Stopped VM"
>>>>>>> 20ff0cfecde5e61ef7a31d7482cd3a14d999820a


