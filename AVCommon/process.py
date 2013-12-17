__author__ = 'fabrizio'

import time
from AVCommon.logger import logging


def wait_timeout(proc, seconds):
    """Wait for a process to finish, or raise exception after timeout"""
    start = time.time()
    end = start + seconds
    interval = min(seconds / 1000.0, .25)

    logging.debug("DBG wait for: %s sec" % seconds)
    while True:
        result = proc.poll()
        if result is not None:
            return result
        if time.time() >= end:
            proc.kill()
            logging.debug("DBG Process timed out, killed")
            break
        time.sleep(interval)