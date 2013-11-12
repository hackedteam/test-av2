import os
import sys
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import command

class Command_INTERNET_OFF(command.ServerCommand):
    """ Executes a program on a vm """

    def execute(self, args):
        """ server side """

        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"

        ret = os.system("sudo ../AVMaster/net_disable.sh")

        if ret == 0:
            return True, "Internet OFF"
        else:
            return False, "Failed Internet OFF"


