__author__ = 'fabrizio'

import os
import sys
from AVCommon.logger import logging
from time import sleep
from AVCommon import mq

def convert_processes(procs):
    processes = []
    if not procs:
        return None

    lines = procs.split("\n")
    if not lines:
        return None

    for l in lines[1:]:
        proc = {}
        tokens = l.split(", ", 2)
        for t in tokens:
            try:
                k,v = t.split("=", 1)
                if k == "cmd":
                    k = "name"
                proc[k] = v
            except:
                pass
        if proc:
            processes.append(proc)

    logging.debug("processes: %s" % processes)
    return processes