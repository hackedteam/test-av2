import os
import sys

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import Protocol

from lib.core.VMachine import VMachine
from lib.core.VMManager import vSphere, VMRun

vmman = VMRun(vm_conf_file)

class AVMachine(object):
    name = ""

    """docstring for AVMachine"""
    def __init__(self, name):
        self.name = name



