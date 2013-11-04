import os
import sys
import threading
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVCommon.protocol import Protocol
from AVMaster.vm_manager import VMManager


class AVMachine(threading.Thread):
    """docstring for AVMachine"""
    name = ""

    def __init__(self, mq, name, procedure):
        super(AVMachine, self).__init__()
        self.name = name
        self.procedure = procedure
        self.mq = mq

        mq.add_client(name)
        mq.add_client("avmanager_%s" % name)

        self.p = Protocol(mq, name)
        #self.vmman = VMManager(name, "../AVMaster/conf/vms.cfg")

        logging.debug("added avMachine: %s" % name)


    def manage_answer(self, msg):
        """ gives the answer to the current command """
        self.cmd.on_answer(msg)

    def run(self):
        while not exit:
            rec = self.mq.receive_command.receive_client(blocking=True, timeout=0)
            logging.debug("received command: %s" % self.name)
            if rec is not None:
                logging.debug("- CLIENT RECEIVED %s %s" % (rec, type(rec)))


    def execute_next_command(self):
        """ extract and send or execute the next command in the procedure"""
        if not self.procedure:
            return None

        self.cmd = self.procedure.next_command()
        if self.cmd.side == "client":
            p = Protocol(self.mq, self.name)
            p.send_next_command(self.cmd)
        else:




