import logging

def on_init(vm, args):
    """ server side """
    pass

def on_answer(vm, success, answer):
    """ server side """
    pass

def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    START AGENT")
    assert vm, "null vm"

    return True, "AGENT STARTED"


