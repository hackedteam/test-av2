__author__ = 'zeno'

from AVCommon.logger import logging
import time
import glob
import os
import platform

from AVCommon import command
from AVAgent import build

def on_init(protocol, args):
    return True

def on_answer(vm, success, answer):
    pass

def execute(vm, args):
    if platform.release() == "XP":
        start_dir = '%s\\Start Menu\\Programs\\Startup' % os.environ['userprofile']
    else:
        start_dir = "%s\\Microsoft\\Windows\\Start Menu\\Programs\\Startup" % os.environ['appdata']

    if args == "STARTUP":
        args = ["%s\\*" % start_dir]
    if args == "STARTUP_EXE":
        args = ["%s\\*.exe" % start_dir]
    logging.debug("Listing files: %s" % args)
    files = [ glob.glob(f) for f in args ]
    if [] in files:
        return True, []

    flat = [ item for sublist in files for item in sublist ]
    if isinstance(args, list) and len(args) == 1:
        flat = [ item.split("\\")[-1] for item in flat ]
    logging.debug("files: %s, expanded files: %s" % (files, flat))

    return True, flat