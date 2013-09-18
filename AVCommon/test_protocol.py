from Protocol import Protocol
from Command import Command
from MQ import MQStar
import threading


def server(mq, clients, commands):
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
        rec = mq.receiveServer(blocking=True, timeout=5)
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

def test_Protocol():
    host = "localhost"
    mq1 = MQStar(host)
    mq1.clean()
    c = "client1"
    mq1.addClient(c)

    commands = [("START", None, None), ("END", None, None)]
    thread1 = threading.Thread(target=server, args=(mq1, [c], commands))
    thread1.start()
    cmdStart = Command.unserialize(('START', True, 'nothing else to say'))

    print "- CLIENT: ", c
    pc = Protocol(mq1, c)
    exit = False
    while not exit:
        received = pc.receiveCommand()
        print "- CLIENT RECEIVED: ", received
        if received.name == "END":
            exit = True

if __name__ == '__main__':
    test_Protocol()