from MQ import MQStar


def test_MQ():
    host = "localhost"
    mq = MQStar(host)

    clients = ["c1", "c2", "c3"]
    mq.addClients(clients)

    for c in clients:
        mq.sendToServer(c, "STARTED")

    for i in range(len(clients)):
        c, m = mq.serverRead()
        assert(c in clients)
        assert(m == "STARTED")
        mq.sendToClient(c, "END")

    for c in clients:
        m = mq.clientRead()
        assert(m == "END")


if __name__ == '__main__':
    test_MQ()
