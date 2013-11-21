import logging
from time import sleep
import random


def execute(vm, args):
    if isinstance(args, int):
        #"Sleep needs only an int as argument"
        logging.debug("    CS Sleep for %s" % args)
        sleep(args)
        return True, "slept for %s" % args

    elif isinstance(args, list) and len(args) == 2:
        min, max = args
        logging.debug("    CS Sleep for random %s,%s" % (min, max))
        n = random.randint(min, max)
        sleep(n)
        return True, "slept for %s" % n

    return False, "Wrong way to use SLEEP"