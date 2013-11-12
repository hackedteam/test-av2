import logging
from time import sleep

def execute(vm, args):
    assert isinstance(args, int), "Sleep needs only an int as argument"
    logging.debug("    CS Sleep for %s" % args)
    sleep(args)
    return True, "slept for %s" % args


