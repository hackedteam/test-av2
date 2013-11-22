import os
import sys
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVCommon.protocol import Protocol


class Dispatcher(object):
    """docstring for Dispatcher"""

    vms = []

    def __init__(self, mq, vms, report=None, timeout=0):
        self.vms = vms
        self.mq = mq
        self.report = report
        self.timeout = timeout

    def dispatch(self, procedure, ):
        global received
        exit = False

        procedure.add_begin_end()

        logging.debug("- SERVER len(procedure): %s" % len(procedure))
        self.num_commands = len(procedure)

        if self.report:
            self.report.init(procedure)

        av_machines = {}
        for vm in self.vms:
            av_machines[vm] = Protocol(self.mq, vm, procedure)

        for p in av_machines.values():
            #a.start()
            self.mq.clean(p)
            r = p.send_next_command()
            c = p.last_command
            if self.report:
                self.report.sent(p, str(c))
            logging.debug("- SERVER SENT: %s" % c)

        ended = 0
        answered = 0
        while not exit and ended < len(self.vms):
            rec = self.mq.receive_server(blocking=True, timeout=self.timeout)
            if rec is not None:
                logging.debug("- SERVER RECEIVED %s %s" % ( str(rec)[:50], type(rec)))
                c, msg = rec
                p = av_machines[c]
                answer = p.receive_answer(c, msg)

                if self.report:
                    from AVCommon import command
                    self.report.received(c, command.unserialize(msg))

                if answer.success == None:
                    logging.debug("- SERVER IGNORING")
                    continue

                answered += 1
                #logging.debug("- SERVER RECEIVED ANSWER: %s" % answer.success)
                if answer.name == "END":
                    ended += 1
                    logging.debug("- SERVER RECEIVE END")
                elif answer.success:
                    r = p.send_next_command()
                    cmd = p.last_command
                    if self.report:
                        self.report.sent(p.vm, str(cmd))
                    logging.debug("- SERVER SENT: %s, %s" % (c, cmd))
                    if not r:
                        logging.debug("- SERVER SENDING ERROR, ENDING")
                        ended += 1
                else:
                    ended += 1
                    logging.debug("- SERVER RECEIVE ERROR, ENDING")

            else:
                logging.debug("- SERVER RECEIVED empty")
                exit = True


        #if self.report:
        #    self.report.dump()

        logging.debug("answered: %s, ended: %s, num_commands: %s" % ( answered, ended, self.num_commands))
        assert ended == len(self.vms), "answered: %s, ended: %s, num_commands: %s" % ( answered, ended, len(self.vms))
        #assert answered >= (len(self.vms) * (self.num_commands)), "answered: %s, len(vms): %s, num_commands: %s" % (answered , len(self.vms), self.num_commands)
        return answered