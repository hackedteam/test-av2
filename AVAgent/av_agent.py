__author__ = 'fabrizio'

import sys
print sys.path

import logging, logging.config
import argparse

from AVCommon.mq import MQStar
from AVCommon.protocol import Protocol
from AVCommon import command


commands = ['BUILD']

class AVAgent(object):

    def __init__(self, args):
        self.vm = args.vm
        self.host = args.redis
        self.session = args.session
        logging.debug("vm: %s host: %s" % (self.vm, self.host))
        command.init()
        command.init(None, commands, True)

    def start_agent(self):

        mq = MQStar(self.host, self.session)
        mq.add_client(self.vm)
        pc = Protocol(mq, self.vm)

        logging.info("start receiving commands")
        exit = False
        while not exit:
            received = pc.receive_command()
            logging.debug("- CLIENT RECEIVED: %s" % received)
            if received.name == 'STOP_AGENT':
                exit = True


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

    avagent = AVAgent(args)
    avagent.start_agent()
