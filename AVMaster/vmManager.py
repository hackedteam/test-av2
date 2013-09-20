import os
import sys

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import Protocol


class vmManager:
    def __init__(p):
        assert isinstance(p, Protocol)


