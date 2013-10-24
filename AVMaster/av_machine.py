import os
import sys

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import protocol

from lib.core.VMManager import vSphere, VMRun

vmman = VMRun(vm_conf_file)


class AVMachine(threading.Thread):
    name = ""

    """docstring for AVMachine"""

    def __init__(self, mq, name, procedure):
        self.name = name
        self.procedure = procedure
        self.mq = mq

        mq.add_client(name)
        mq.add_client("avmanager_%s" % name)

        self.p = protocol(mq, name)
        self.vmman = VMManager(name)

    """ gives the answer to the current command """

    def manage_answer(self, msg):
        self.cmd.on_answer(msg)

    def run(self):
        while not exit:
            rec = receive_command.receive_client(blocking=True, timeout=0)
            if rec is not None:
                print "- CLIENT RECEIVED %s %s" % (rec, type(rec))


    """ extract and send or execute the next command in the procedure"""

    def execute_next_command(self):
        if not self.procedure:
            return None

        self.cmd = self.procedure.next_command()
        if self.cmd.side == "client":
            p = protocol(mq, name)
            p.send_next_command(cmd)
        else:
            VMManager.execute(name, cmd)



