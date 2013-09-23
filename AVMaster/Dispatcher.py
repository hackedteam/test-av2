import os
import sys

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import Protocol
from AVCommon import MQStar

class Dispatcher(object):
    """docstring for Dispatcher"""
    def __init__(self, vms, procedure ):
        super(Dispatcher, self).__init__()
        self.arg = arg

    def dispatch(mq, clients, procedure):
        global received
        exit = False
        print "- SERVER ", len(commands)
        numcommands = len(commands)

        p = {}
        for c in clients:
            p[c] = Protocol(mq, c, commands)
            p[c].sendNextCommand()

        ended = 0
        answered = 0
        while not exit and ended < len(clients):
            rec = mq.receiveServer(blocking=True, timeout=10)
            if rec is not None:
                print "- SERVER RECEIVED %s %s" % (rec, type(rec))
                c, msg = rec
                answer = p[c].receiveAnswer(c, msg)
                answered += 1
                print "- SERVER RECEIVED ANSWER: ", answer.success
                if answer.name == "END" or not answer.success:
                    ended += 1
                    "- SERVER RECEIVE END"
                if answer.success:
                    p[c].sendNextCommand()

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
            mq.addClient(vm.name)

        mq.addClient("")

        thread1 = threading.Thread(target=self.server, args=(vm_mq, [c], commands))
        thread1.start()

