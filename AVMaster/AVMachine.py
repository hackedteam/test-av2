import os
import sys

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import Protocol

from lib.core.VMachine import VMachine
from lib.core.VMManager import vSphere, VMRun

vmman = VMRun(vm_conf_file)

class AVMachine(threading.Thread):
    name = ""

    """docstring for AVMachine"""
    def __init__(self, mq, name, procedure):
        self.name = name
        self.procedure = procedure
        self.mq = mq

        mq.addClient(name)
        mq.addClient("avmanager_%s" % name)

        self.p = Protocol(mq, name)
        self.vmman = VMManager(name)


    def run():
        while not exit:
            rec = receiveCommand.receiveClient(blocking=True, timeout=0)
            if rec is not None:
                print "- CLIENT RECEIVED %s %s" % (rec, type(rec))


    def executeNextCommand(self):
        if not self.procedure:
            return None

        cmd = self.procedure.nextCommand()
        if cmd.side == "client":
            p = Protocol(mq, name)
            p.sendNextCommand(cmd)
        else:
            VMManager.execute(name, cmd)



