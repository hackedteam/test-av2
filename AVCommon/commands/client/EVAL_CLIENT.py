from AVCommon.logger import logging

import AVCommon
import AVAgent


def on_init(protocol, args):
    """ server side """
    return True


def on_answer(vm, success, answer):
    """ server side """
    pass


def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    CS Execute")
    assert vm, "null vm"

    ret = eval(args)
    return True, ret


