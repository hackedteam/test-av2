import os
import sys

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)


class VMManager:
    def __init__(name):
        self.name = name

    def execute(cmd):
        pass


