from command import Command
import time, thread

def test_Command():
    host = "localhost"

    s = Command(frm="response")
    c1 = Command(to="server", frm="c1")
    c2 = Command(to="server", frm="c2")

    print dir(s)

    Command(to="c1").send("STARTAGENT")
    Command(to="c2").send("STARTAGENT")

    c1.receive();
    c2.receive();
    c1.send("+STARTED AGENT")
    c2.send("+STARTED AGENT")

    m = s.receive()
    print "RECEIVE: %s" % m
    m = s.receive()
    print "RECEIVE: %s" % m


if __name__ == '__main__':
    test_Command()
