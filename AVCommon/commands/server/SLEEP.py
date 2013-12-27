from AVCommon.logger import logging
from time import sleep
import random
from AVCommon import command
from AVCommon.protocol import Protocol

def execute(vm, protocol, args):
    if isinstance(args, int):
        #"Sleep needs only an int as argument"
        #logging.debug("    CS Sleep for %s" % args)
        sleep(args)
        return True, "slept for %s" % args

    elif isinstance(args, list) and len(args) == 2:
        min, max = args
        #logging.debug("    CS Sleep for random %s,%s" % (min, max))
        assert protocol.id >= 0

        n = 0
        if protocol.id < Protocol.pool:
            n = min +  (max - min) * protocol.id

        sleep(n)
        return True, "slept for %s" % n

    return False, "Wrong way to use SLEEP"