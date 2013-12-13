__author__ = 'zeno'
from AVCommon.logger import logging


def on_init(vm, args):
    """ server side """
    return True


def on_answer(vm, success, answer):
    """ server side """
    pass


def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    STOP_AGENT")
    assert vm, "null vm"

    #TODO: stops a AVAgent on vm
    return True, "AGENT STOPPED"