__author__ = 'fabrizio'

import os, sys
import inspect
#from AVCommon import config

commonname = 'AVCommon'
basedir = None
avcommon = None
avagent = None
avmaster = None

if not basedir:
    cmd_folder = os.path.split(os.path.realpath(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0]
    if cmd_folder not in sys.path:
        sys.path.insert(0, cmd_folder)

    found = False
    folder = cmd_folder
    while not found:
        parent = os.path.split(folder)[0]
        #print "parent: %s" % parent
        if parent not in sys.path:
            sys.path.insert(0, parent)

        for d in [folder, parent]:
            if commonname in os.listdir(d):
                basedir = d
                sys.path.append(d)
                avcommon = __import__("%s" % commonname)
                assert (avcommon)
                print "basedir: %s" % basedir
                found = True
                break

        folder = parent

assert basedir
dir()