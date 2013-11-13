import logging

import AVCommon
import AVAgent

def on_init(vm, args):
    """ server side """
    logging.debug("    CS on_init")

    #TODO: push files on client
    assert vm, "null vm"

def on_answer(vm, success, answer):
    """ server side """
    logging.debug("    CS on_answer")
    assert vm, "null vm"


def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    CS Execute")
    assert vm, "null vm"

    ret = eval(args)
    return True, ret


