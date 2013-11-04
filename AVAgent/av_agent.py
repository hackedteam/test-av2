__author__ = 'fabrizio'

import sys, os
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import logging, logging.config

from AVCommon.procedure import Procedure
from AVCommon.mq import MQStar
from AVCommon.protocol import Protocol
from AVCommon.Command_STOP_AGENT import Command_STOP_AGENT


class AVAgent(object):

    def __init__(self):
        self.vm, self.host, self.session = sys.argv[1:]
        logging.debug("vm: %s host: %s" % (self.vm, self.host))

    def start_agent(self):

        mq = MQStar(self.host, self.session)
        mq.add_client(self.vm)
        pc = Protocol(mq, self.vm)

        logging.info("start receiving commands")
        exit = False
        while not exit:
            received = pc.receive_command()
            logging.debug("- CLIENT RECEIVED: %s" % received)
            if received.name == Command_STOP_AGENT.name:
                exit = True


if __name__ == "__main__":
    logging.config.fileConfig('../logging.conf')
    avagent = AVAgent()
    avagent.start_agent()
