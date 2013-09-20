from vmManager import *

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import Protocol
from AVCommon import MQ


def test_instance():

    host = "localhost"
    mq = MQ.MQStar(host)
    c = "vm"

    p = Protocol.Protocol(mq, c, commands)
    vm = vmManager(p)

if __name__ == '__main__':
    test_instance()
