import os
import sys
import logging


def execute(vm, args):
    """ server side """

    logging.debug("    CS Execute")
    assert vm, "null vm"

    ret = os.system("sudo ../AVMaster/net_disable.sh")

    if ret == 0:
        return True, "Internet OFF"
    else:
        return False, "Failed Internet OFF"


