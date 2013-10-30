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


def server_procedure(mq, clients, procedure):
    global received
    exit = False
    print "- SERVER ", len(procedure)
    numcommands = len(procedure)

    p = {}
    for c in clients:
        p[c] = Protocol(mq, c, procedure)
        p[c].send_next_command()

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

def test_ProtocolProcedure():
    host = "localhost"
    mq1 = MQStar(host)
    mq1.clean()
    c = "client1"
    mq1.add_client(c)

    commands = [("START", None, None), ("END", None, None)]
    procedure = Procedure("PROC", commands)

    thread1 = threading.Thread(target=server_procedure, args=(mq1, [c], procedure))
    thread1.start()

    cmdStart = Command.unserialize(('START', True, 'nothing else to say'))

    assert cmdStart

    print "- CLIENT: ", c
    pc = Protocol(mq1, c)
    exit = False
    while not exit:
        received = pc.receive_command()
        print "- CLIENT RECEIVED: ", received
        if received.name == "END":
            exit = True

def test_ProtocolEval():
    host = "localhost"
    mq = MQStar(host)
    mq.clean()
    c = "client1"
    mq.add_client(c)

    commands = [("EVAL_SERVER", "dir()"),
                ("EVAL_SERVER", "locals()"),
                ("EVAL_SERVER", "__import__('os').getcwd()"),
                ("EVAL_SERVER", "*'END'")]
    procedure = Procedure("PROC", commands)

    p = Protocol(mq, c, procedure)

    print("---- START SENDING ----")
    for r in p.next():
        logging.debug("ret: %s" % r)

    print("---- START RECEIVING ----")
    exit = False
    while not exit:
        rec = mq.receive_server(blocking=True, timeout=10)
        if rec:
            print "- SERVER RECEIVED %s %s" % (rec, type(rec))
            c, msg = rec
            answer = p.manage_answer(c, msg)
            print "- SERVER RECEIVED ANSWER: ", answer.success
            if answer.payload == "END" or not answer.success:
                "- SERVER RECEIVE END"
            #if answer.success:
            #   p.send_next_command()

        else:
            print "- SERVER RECEIVED empty"
            exit = True
    print("---- STOP RECEIVING ----")

if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    #test_ProtocolProcedure()
    test_ProtocolEval()
