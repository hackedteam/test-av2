import sys
sys.path.append("../AVCommon")

import Protocol
import MQ
from Command import Command

class Procedure :
    """docstring for Procedure"""
    def __init__(self, name, proc=[]):
        self.name = name
        self.proc = [ Command.unserialize(c) for c in proc ]
