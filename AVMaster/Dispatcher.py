import os
import sys

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import MQStar


class Dispatcher(object):
    """docstring for Dispatcher"""
    def __init__(self, vms, procedure):
        super(Dispatcher, self).__init__()
        self.vms = vms
        self.procedure = procedure

    def dispatch(mq, clients, procedure):
        global received
        exit = False
        print "- SERVER ", len(commands)
        num_commands = len(commands)

        av_machines = []
        for c in clients:
            av_machines.append(AVMachine(mq, c, procedure))

        for a in avmachines:
            a.start()
            a.execute_next_command()

        ended = 0
        answered = 0
        while not exit and ended < len(clients):
            rec = mq.receive_server(blocking=True, timeout=10)
            if rec is not None:
                print "- SERVER RECEIVED %s %s" % (rec, type(rec))
                c, msg = rec
                answer = p[c].manage_answer(c, msg)
                answered += 1
                print "- SERVER RECEIVED ANSWER: ", answer.success
                if answer.name == "END" or not answer.success:
                    ended += 1
                    "- SERVER RECEIVE END"
                if answer.success:
                    p[c].send_next_command()

            else:
                print "- SERVER RECEIVED empty"
                exit = True

        print answered, ended, numcommands
        assert(ended == len(clients))
        assert(answered == (len(clients) * numcommands))

    def startServer(self):
        host = "localhost"
        mq = MQStar(host)
        mq.clean()
        for vm in self.vms:
            mq.add_client(vm.name)

        mq.add_client("")

        thread1 = threading.Thread(target=self.server, args=(vm_mq, [c], commands))
        thread1.start()

