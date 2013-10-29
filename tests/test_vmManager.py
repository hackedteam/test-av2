import sys
import os

sys.path.append("../AVCommon")
sys.path.append("AVCommon")

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import mq
from AVMaster.vm_manager import VMManager


def test_instance():
    vm = VMManager()
    #print vm, dir(vm)
    vm.test_missing
    vm.test_new_command("primo", 2)

if __name__ == '__main__':
    test_instance()
