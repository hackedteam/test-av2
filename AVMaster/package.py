__author__ = 'fabrizio'

import os, sys
from AVCommon import config

commonname = 'AVCommon'
basedir = None
avcommon = None
avagent = None
avmaster = None

if not basedir:
    localdir = os.getcwd()
    parent = os.path.split(os.getcwd())[0]

    for d in [ localdir, parent ]:
        if commonname in os.listdir(d):
            basedir = d
            sys.path.append(d)
            avcommon = __import__("%s" % commonname)
            assert(avcommon)
            break

assert basedir
dir()