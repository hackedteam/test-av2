import os
import sys

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import Protocol


class AVMachine(object):
    """docstring for AVMachine"""
    def __init__(self, arg):
        super(AVMachine, self).__init__()
        self.arg = arg

