import logging

import AVCommon
import AVAgent

def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    CS Execute")
    assert vm, "null vm"

    ret = eval(args)
    return True, ret


