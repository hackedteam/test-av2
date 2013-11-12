import os
import sys
import logging


""" Executes a program on a vm """

def execute(vm, args):
    """ server side """

    logging.debug("    CS Execute")
    assert vm, "null vm"

    ret = os.system("sudo ../AVMaster/net_enable.sh")

    if ret == 0:
        return True, "Internet ON"
    else:
        return False, "Failed Internet ON"


