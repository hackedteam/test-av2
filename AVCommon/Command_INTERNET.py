import os
import sys
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import command

class Command_INTERNET(command.ServerCommand):
    """ Executes a program on a vm """

    def execute(self, args):
        """ server side """

        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"
        assert isinstance(args, bool), "INTERNET argument must be boolean"
#        assert ["on","off"] in args and len(args) == 1, "INTERNET accepts on/off as parameter"

        if args == True:
            cmd = "sudo ../AVMaster/net_enable.sh"
        elif args == False:
            cmd = "sudo ../AVMaster/net_disable.sh"
        else:
            return False, "Failed Internet ON (wrong parameter)"

        ret = os.system(cmd)

        if ret == 0:
            return True, "Internet %s" % args
        else:
            return False, "Failed Internet %s" % args


