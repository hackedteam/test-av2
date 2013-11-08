import os
import sys
import threading
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVCommon.protocol import Protocol
import AVMaster.vm_manager


class AVMachine(threading.Thread):
    """docstring for AVMachine"""
    name = ""

    def __init__(self, mq, name, procedure):
        super(AVMachine, self).__init__()
        self.name = name
        self.mq = mq

        mq.add_client(name)
        #mq.add_client("avmanager_%s" % name)

        self.protocol = Protocol(mq, name, procedure)
        #self.vmman = VMManager(name, "../AVMaster/conf/vms.cfg")

        logging.debug("added avMachine: %s" % name)


    def manage_answer(self, msg):
        """ gives the answer to the current command """
        return self.protocol.receive_answer(self.name, msg)

    def run(self):
        logging.debug("running")
        while not exit:
            rec = self.mq.receive_command.receive_client(blocking=True, timeout=0)
            logging.debug("received command: %s" % self.name)
            if rec is not None:
                logging.debug("- CLIENT RECEIVED %s %s" % (rec, type(rec)))


    def execute_next_command(self):
        """ extract and send or execute the next command in the procedure"""
        ret = self.protocol.send_next_command()
        last =  self.protocol.last_command

        return ret, last
        #    logging.debug("sent command")
        #logging.debug("sent all commands: %s" % self.name)