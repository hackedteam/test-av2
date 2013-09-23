import os
import sys

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import Protocol


class VMManager:
    def __init__(protocol):
        assert isinstance(protocol, Protocol)

