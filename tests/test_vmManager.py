import sys
import os

sys.path.append("../AVCommon")
sys.path.append("AVCommon")

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import mq


def test_instance():
    host = "localhost"
    m = mq.MQStar(host)
    c = "vm"


if __name__ == '__main__':
    test_instance()
