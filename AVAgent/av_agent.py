__author__ = 'fabrizio'

import sys, os
import argparse
import shutil
import inspect
import signal
import time

inspect_getfile = inspect.getfile(inspect.currentframe())
cmd_folder = os.path.split(os.path.realpath(os.path.abspath(inspect_getfile)))[0]
os.chdir(cmd_folder)

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
parent = os.path.split(cmd_folder)[0]
if parent not in sys.path:
    sys.path.insert(0, parent)

from AVCommon import logger

from AVCommon.mq import MQStar
from AVCommon.protocol import Protocol
from AVCommon import command
from AVCommon.procedure import Procedure
from AVCommon import config

class MQFeedProcedure(object):
    protocol = None

    def receive_client(self, client, blocking=False, timeout=60):
        cmd = self.protocol.procedure.next_command()
        logging.debug("receive_client: %s, %s" % (client, cmd))
        if cmd:
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

def remove_running(vm):
    logging.info("remove running")
    filepid = "running/avagent.%s.running" % vm
    logging.debug("filepid: %s" % filepid)
    os.remove(filepid)

def check_running(vm):
    if not os.path.exists("running"):
        os.mkdir("running")

    filepid = "running/avagent.%s.running" % vm
    if os.path.exists(filepid):
        return True

    f = open(filepid, "w+")
    f.write("%s\r\n" % os.getpid())
    f.close()
    return False

class AVAgent(object):
    def __init__(self, vm, redis='localhost', session=None):
        self.vm = vm
        self.host = redis
        self.session = session
        command.init()
        shutil.rmtree('build', ignore_errors=True)
        if os.path.exists(config.basedir_crop):
            shutil.rmtree(config.basedir_crop)

        if 'logging' not in locals():

            from AVCommon.logger import logging
            locals()['logging']=logging

        logging.debug("vm: %s host: %s session: %s" % (self.vm, self.host, session))

        command.context["report"] = self.report

    def __del__(self):
        remove_running(self.vm)

    def report(self, message):
        logging.debug("report: %s" % message)
        self.pc.send_answer(command._factory("BUILD", None, None, message, self.vm))

    def start_agent(self, mq=None, procedure=None, force=False):

        if not force and check_running(self.vm):
            logging.fatal("already running")
            exit = True
            return False

        class D:
            pass
        d = D()

        if not mq:
            mq = MQStar(self.host, self.session)
            d.mq = mq
            self.pc = Protocol(d, self.vm)
        else:
            assert procedure
            self.pc = Protocol(d, self.vm, procedure=procedure)
            mq.protocol = self.pc
            logging.debug("mq: %s pc:%s" % (mq.protocol.procedure, self.pc.procedure))

        mq.add_client(self.vm)
        mq.notify_connection(self.vm)

        logging.info("start receiving commands")
        exit = False
        while not exit:
            logging.debug("- CLIENT %s LISTENING" % self.vm)
            received = self.pc.receive_command()
            logging.debug("- CLIENT %s EXECUTED: %s" % (self.vm, received))
            if received.name == 'STOP_AGENT':
                exit = True

        logging.info("stop receiving commands")
        remove_running(self.vm)


def start_agent(args, force=False):
    vm, redis, session = args
    avagent = AVAgent(vm, redis, session)
    avagent.start_agent(force=force)


def start_agent_args(vm, redis, session, force=False):
    avagent = AVAgent(vm, redis, session)
    avagent.start_agent(force=force)


if __name__ == "__main__":


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

    report = time.strftime("%y%m%d", time.localtime(time.time()))
    logger.init(report)
    from AVCommon.logger import logging
    globals()['logging']=logging
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
    Procedure.check()

    try:
        avagent = AVAgent(args.vm, args.redis, args.session)
        avagent.start_agent(mq, procedure)
    except:
        logging.exception("FATAL")
