__author__ = 'fabrizio'

import sys, os

import logging, logging.config
import argparse
import shutil
import inspect

inspect_getfile = inspect.getfile(inspect.currentframe())
cmd_folder = os.path.split(os.path.realpath(os.path.abspath(inspect_getfile)))[0]
os.chdir(cmd_folder)

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
parent = os.path.split(cmd_folder)[0]
if parent not in sys.path:
    sys.path.insert(0, parent)

from AVCommon.mq import MQStar
from AVCommon.protocol import Protocol
from AVCommon import command
from AVCommon.procedure import Procedure

commands = ['BUILD', 'GET', 'SET']


class MQFeedProcedure(object):
    protocol = None

    def receive_client(self, client, blocking=False, timeout=60):
        cmd = self.protocol.procedure.next_command()
        logging.debug("receive_client: %s, %s" % (client, cmd))
        return cmd.serialize()

    def send_client(self, client, message):
        pass

    def receive_server(self, blocking=False, timeout=10):
        pass

    def send_server(self, client, message):
        logging.debug("send_server: %s" % message)
        pass

    def add_client(self, vm):
        pass


class AVAgent(object):
    def __init__(self, vm, redis='localhost', session=None):
        self.vm = vm
        self.host = redis
        self.session = session
        command.init()
        shutil.rmtree('build', ignore_errors=True)
        logging.debug("vm: %s host: %s session: %s" % (self.vm, self.host, session))

    def start_agent(self, mq=None, procedure=None):
        if not mq:
            mq = MQStar(self.host, self.session)
            pc = Protocol(mq, self.vm)
        else:
            assert procedure
            pc = Protocol(mq, self.vm, procedure=procedure)
            mq.protocol = pc
            logging.debug("mq: %s pc:%s" % (mq.protocol.procedure, pc.procedure))
        mq.add_client(self.vm)

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


def start_agent_args(vm, redis, session):
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
    parser.add_argument('-r', '--procedure', default=False,
                        help="procedure to call ")
    parser.add_argument('-f', '--procedure_file', default=False,
                        help="procedure file to read ")

    args = parser.parse_args()
    logging.debug(args)

    mq = None
    procedure = None
    if args.procedure and args.procedure_file:
        logging.info("Procedure %s" % args.procedure)
        path = os.getcwd()
        procs = Procedure.load_from_file(args.procedure_file)
        logging.debug("%s" % procs)
        procedure = procs[args.procedure]
        mq = MQFeedProcedure()

    avagent = AVAgent(args.vm, args.redis, args.session)
    avagent.start_agent(mq, procedure)
