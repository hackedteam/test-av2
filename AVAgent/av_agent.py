__author__ = 'fabrizio'

import sys, os

import logging, logging.config
import argparse

sys.path.append(os.path.split(os.getcwd())[0])

from AVCommon.mq import MQStar
from AVCommon.protocol import Protocol
from AVCommon import command

commands = ['BUILD', 'GET', 'SET']

class AVAgent(object):

    def __init__(self, vm, redis='localhost', session=None):
        self.vm = vm
        self.host = redis
        self.session = session
        logging.debug("vm: %s host: %s session: %s" % (self.vm, self.host, session))
        command.init()
        command.init("AVAgent", commands, True)

    def start_agent(self):

        mq = MQStar(self.host, self.session)
        mq.add_client(self.vm)
        pc = Protocol(mq, self.vm)

        logging.info("start receiving commands")
        exit = False
        while not exit:
            logging.debug("- CLIENT %s LISTENING" % self.vm)
            received = pc.receive_command()
            logging.debug("- CLIENT %s EXECUTED: %s" % (self.vm, received))
            if received.name == 'STOP_AGENT':
                exit = True

        logging.info("stop receiving commands")

def start_agent(args):
    vm, redis, session = args
    avagent = AVAgent(vm, redis, session)
    avagent.start_agent()

if __name__ == "__main__":
    logging.config.fileConfig('../logging.conf')

    parser = argparse.ArgumentParser(description='AVMonitor agent.')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Verbose")
    parser.add_argument('-m', '--vm', required=True,
                        help="Virtual Machine of the operation")
    parser.add_argument('-d', '--redis', default="localhost",
                        help="redis host")
    parser.add_argument('-s', '--session', default=False,
                        help="session redis mq ")

    args = parser.parse_args()
    logging.debug(args)

    avagent = AVAgent(args.vm, args.redis, args.session)
    avagent.start_agent()
