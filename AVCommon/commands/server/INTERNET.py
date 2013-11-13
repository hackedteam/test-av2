import os
import sys
import logging


""" Executes a program on a vm """

def execute(vm, args):
    """ server side """

    logging.debug("    CS Execute")
    assert vm, "null self.vm"
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


