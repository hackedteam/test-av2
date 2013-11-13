__author__ = 'zeno'
import logging

def on_init(vm, args):
    """ server side """
    logging.debug("    CS on_init")

def on_answer(vm, success, answer):
    """ server side """
    logging.debug("    CS on_answer")

def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    STOP_AGENT")
    assert vm, "null vm"

    #TODO: stops a AVAgent on vm
    return True, ""