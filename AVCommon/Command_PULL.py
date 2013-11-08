import os
import sys
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import command
from AVMaster import vm_manager


#TODO
#noinspection PyPep8Naming
class Command_PULL(command.ServerCommand):
    """ Pulls a set of files from a vm """

    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"
        assert len(args) > 1

        #TODO pull files from self.vm
        src, dst = args
        vm_manager.execute(self.vm, "copyFileFromGuest", src, dst)
        return True, "PULLED %s" % args[0]
