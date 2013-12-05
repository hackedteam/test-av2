import os
import sys
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVCommon.protocol import Protocol
from AVCommon import command
from AVMaster import report

def red(msg, max_len=50):
    s = str(msg)
    if len(s) < max_len:
        return s

    return "%s ..." %  s[:50]

class Dispatcher(object):
    """docstring for Dispatcher"""

    vms = []

    def __init__(self, mq, vms, timeout=0):
        self.vms = vms
        self.mq = mq
        self.timeout = timeout

    def end(self, c):
        logging.debug("- SERVER END: %s" % c)
        self.ended.add(c)
        if self.pool:
            m = self.pool.pop()
            logging.debug("pool popped: %s" % m)
            self.start(m)

    def start(self, p):
        logging.debug("- SERVER START: %s" % p)
        self.mq.clean(p)
        r = p.send_next_command()
        c = p.last_command

        report.sent(p.vm, str(c))
        logging.info("- SERVER SENT: %s" % c)

    def pool_start(self, machines, size):
        logging.debug("pool start, size: %s" % size )
        self.pool = machines
        for i in range(size):
            m = self.pool.pop()
            self.start(m)

    def dispatch(self, procedure, pool=0 ):
        global received
        exit = False

        procedure.add_begin_end()

        logging.debug("- SERVER len(procedure): %s" % len(procedure))
        self.num_commands = len(procedure)

        report.init(procedure.name)

        logging.debug("self.vms: %s" % self.vms)
        av_machines = {}
        for vm in self.vms:
            av_machines[vm] = Protocol(self, vm, procedure)

        if pool == 0:
            pool = len(self.vms)
        self.pool_start(av_machines.values(), pool)

        self.ended = set()
        answered = 0
        while not exit and len(self.ended) < len(self.vms):
            rec = self.mq.receive_server(blocking=True, timeout=self.timeout)
            if rec is not None:
                c, msg = rec
                logging.info("- SERVER RECEIVED %s" % ( red(command.unserialize(msg))))
                p = av_machines[c]
                answer = p.receive_answer(c, msg)

                report.received(c, command.unserialize(msg))

                if answer.success == None:
                    logging.info("- SERVER IGNORING")
                    continue

                answered += 1
                #logging.debug("- SERVER RECEIVED ANSWER: %s" % answer.success)
                if answer.name == "END":
                    self.end(c)
                    logging.info("- SERVER RECEIVE END: %s" % self.ended)
                elif answer.success:
                    r = p.send_next_command()
                    cmd = p.last_command

                    report.sent(p.vm, str(cmd))

                    logging.info("- SERVER SENT: %s, %s" % (c, cmd))
                    if not r:
                        logging.info("- SERVER SENDING ERROR, ENDING")
                        self.end(c)
                else:
                    self.end(c)
                    logging.info("- SERVER RECEIVE ERROR, ENDING: %s" %c)

            else:
                logging.info("- SERVER RECEIVED empty")
                exit = True


        #if self.report:
        #    self.report.dump()

        logging.debug("answered: %s, ended: %s, num_commands: %s" % ( answered, len(self.ended), self.num_commands))
        assert len(self.ended) == len(self.vms), "answered: %s, ended: %s, num_commands: %s" % ( answered, len(self.ended), len(self.vms))
        #assert answered >= (len(self.vms) * (self.num_commands)), "answered: %s, len(vms): %s, num_commands: %s" % (answered , len(self.vms), self.num_commands)
        return answered