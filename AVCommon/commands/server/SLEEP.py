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

        n = min

        if protocol.id < Protocol.pool:
            n = min +  (float(max - min)  * protocol.id) / (Protocol.pool - 1 )

        n = int(n)
        logging.debug("%s  protocol.id: %s Protocol.pool: %s n: %s" %( vm, protocol.id, Protocol.pool, n))

        sleep(n)
        return True, "slept for %s" % n

    return False, "Wrong way to use SLEEP"