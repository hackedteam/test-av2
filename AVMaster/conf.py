__author__ = 'fabrizio'

import os, sys

verbose = False
basedir = False

commonname = 'AVCommon'
basedir = None

if not basedir:
    localdir = os.getcwd()
    parent = os.path.split(os.getcwd())[0]

    for d in [ localdir, parent ]:
        if commonname in os.listdir(d):
            basedir = d
            sys.path.append(d)
            m = __import__("%s.command" % commonname)
            assert(m)
            break

assert basedir