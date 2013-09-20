import os, sys
prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import Protocol
from AVCommon import MQ
from AVCommon.Command import Command

class Procedure :
    """docstring for Procedure"""
    def __init__(self, name, proc=[]):
        self.name = name
        self.proc = [ Command.Command.unserialize(c) for c in proc ]
