import os
import sys

sys.path.append("../AVCommon")
prev = os.path.join(os.getcwd(), "..")

if not prev in sys.path:
    sys.path.append(prev)

from AVCommon.mq import MQStar
from av_machine import AVMachine


class Dispatcher(object):
    """docstring for Dispatcher"""

    def __init__(self, vms):
        super(Dispatcher, self).__init__()
        self.vms = vms

    def dispatch(self, mq, clients, procedure):
        global received
        exit = False
        print "- SERVER ", len(procedure)
        self.num_commands = len(procedure)

        av_machines = {}
        for c in clients:
            av_machines[c] = AVMachine(mq, c, procedure)

        for a in av_machines.values():
            a.start()
            a.execute_next_command()

        ended = 0
        answered = 0
        while not exit and ended < len(clients):
            rec = mq.receive_server(blocking=True, timeout=10)
            if rec is not None:
                print "- SERVER RECEIVED %s %s" % (rec, type(rec))
                c, msg = rec
                m = av_machines[c]
                answer = m.receive_answer(msg)
                answered += 1
                print "- SERVER RECEIVED ANSWER: ", answer.success
                if answer.name == "END" or not answer.success:
                    ended += 1
                    print "- SERVER RECEIVE END"
                if answer.success:
                    p[c].send_next_command()

            else:
                print "- SERVER RECEIVED empty"
                exit = True

        print answered, ended, numcommands
        assert (ended == len(clients))
        assert (answered == (len(clients) * numcommands))

    def startServer(self):
        host = "localhost"
        mq = MQStar(host)
        mq.clean()
        for vm in self.vms:
            mq.add_client(vm.name)

        mq.add_client("")

        thread1 = threading.Thread(target=self.server, args=(vm_mq, [c], commands))
        thread1.start()

