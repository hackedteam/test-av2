from Protocol import Protocol
from Command import Command
from MQ import MQStar
import threading

def server(mq, clients, commands):
    global received
    exit = False
    print "SERVER"
    p = {}
    for c in clients:
        p[c] = Protocol(mq, c, commands)
        p[c].sendNextCommand()

    while not exit:
        rec = mq.receiveServer(blocking=True, timeout = 5)
        if rec is not None:
            print "SERVER RECEIVED %s %s" % (rec, type(rec))
            c, msg = rec
            answer = p[c].receiveAnswer(c, msg)
            #p[c].sendNextCommand()
        else:
            print "SERVER RECEIVED empty"
            exit = True

def test_Protocol():
    host = "localhost"
    mq1 = MQStar(host)
    mq1.clean()
    c = "client1"
    mq1.addClient(c)

    commands = [ ("START",None,None), ("END",None,None) ]
    thread1 = threading.Thread(target=server, args=(mq1, [c], commands))
    thread1.start()
    cmdStart = Command.unserialize(('START','OK','nothing else to say'))

    print "CLIENT: ", c
    pc = Protocol(mq1, c)
    received = pc.receiveCommand()
    print "CLIENT RECEIVED: ", received

if __name__ == '__main__':
    test_Protocol()