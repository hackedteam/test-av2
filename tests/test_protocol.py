import sys
sys.path.append("../AVCommon")
sys.path.append("../AVMaster")

from Protocol import Protocol
from Command import Command
from MQ import MQStar
from Procedure import Procedure
import threading
import logging
import logging.config


def server(mq, clients, commands):
    global received
    exit = False
    print "- SERVER ", len(commands)
    numcommands = len(commands)

    p = {}

    cmd=commands.pop(0)
    for c in clients:
        p[c] = Protocol(mq, c)
        p[c].sendCommand(cmd)

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

    assert cmdStart

    print "- CLIENT: ", c
    pc = Protocol(mq1, c)
    exit = False
    while not exit:
        received = pc.receiveCommand()
        print "- CLIENT RECEIVED: ", received
        if received.name == "END":
            exit = True

def serverProcedure(mq, clients, procedure):
    global received
    exit = False
    print "- SERVER ", len(procedure)
    numcommands = len(procedure)

    p = {}
    for c in clients:
        p[c] = Protocol(mq, c, procedure)
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

def test_ProtocolProcedure():
    host = "localhost"
    mq1 = MQStar(host)
    mq1.clean()
    c = "client1"
    mq1.addClient(c)

    commands = [("START", None, None), ("END", None, None)]
    procedure = Procedure("PROC", commands)

    thread1 = threading.Thread(target=serverProcedure, args=(mq1, [c], procedure))
    thread1.start()

    cmdStart = Command.unserialize(('START', True, 'nothing else to say'))

    assert cmdStart

    print "- CLIENT: ", c
    pc = Protocol(mq1, c)
    exit = False
    while not exit:
        received = pc.receiveCommand()
        print "- CLIENT RECEIVED: ", received
        if received.name == "END":
            exit = True


if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    #test_Protocol()
    test_ProtocolProcedure()
