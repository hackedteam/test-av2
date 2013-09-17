from MQ import MQStar


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
    test_MQ()
    test_MultipleMQ()
