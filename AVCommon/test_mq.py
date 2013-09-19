from MQ import MQStar
import time
import threading
import logging, sys
import logging.config

received = []


def server(mq):
    global received
    exit = False
    print "SERVER"
    while not exit:
        rec = mq.receiveServer(blocking=True, timeout=5)
        if rec is not None:
            logging.debug("%s %s" % (rec, type(rec)))
            c, m = rec
            print "SERVER RECEIVED: %s>%s" % (c, m)
            received.append(m)

            if m == "STOP":
                logging.debug("EXITING")
                exit = True
        else:
            exit = True


def test_blockingMQ():
    global received

    host = "localhost"
    mq1 = MQStar(host)
    mq2 = MQStar(host, session=mq1.session)

    c = "client1"

    mq1.addClient(c)
    thread1 = threading.Thread(target=server, args=(mq1,))
    thread1.start()

    mq2.sendServer(c, "WORKS")
    time.sleep(1)
    mq2.sendServer(c, "FINE TO THE")
    time.sleep(1)
    mq2.sendServer(c, "STOP")

    print "RECEIVED: ", received
    assert len(received) == 3

def test_MultipleMQ():
    host = "localhost"
    mq1 = MQStar(host)
    mq2 = MQStar(host, session=mq1.session)

    client, message = "c1", "HELLO"
    mq1.sendServer(client, message)
    c, m = mq2.receiveServer()
    assert (c == client)
    assert (m == message)


def test_MQ():
    host = "localhost"
    mq = MQStar(host)

    mq.clean()

    clients = ["c1", "c2", "c3"]
    mq.addClients(clients)

    for c in clients:
        mq.sendServer(c, "STARTED")

    for i in range(len(clients)):
        c, m = mq.receiveServer()
        assert(c in clients)
        assert(m == "STARTED")
        mq.sendClient(c, "END %s" % i)

    for c in clients:
        m = mq.receiveClient(c)
        print m
        assert(m.startswith("END "))

if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    test_MQ()
    test_MultipleMQ()
    test_blockingMQ()
