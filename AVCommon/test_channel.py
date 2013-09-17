from Channel import Channel
import time
import thread
from redis import StrictRedis
import ast

"""
execute via nose or py.test
"""

count = 0


def server(s):
    global count
    for c, m in s.read():
        print "RECEIVED: %s | %s" % (c, m)
        count += 1


def test_Redis():
    host = "localhost"
    r = StrictRedis(host, socket_timeout=60)
    msg = "Hello world"

    r.delete("channel")
    r.rpush("channel", msg)
    m = r.lpop("channel")
    print m
    assert(m == msg)

    r.rpush("channel", [1, 2, 3])
    m = ast.literal_eval(r.lpop("channel"))
    print m, type(m)


def test_ChannelList():
    global count
    channel = "response"
    host = "localhost"

    s = Channel(host, channel)
    c1 = Channel(host, channel + ".c1")
    c2 = Channel(host, channel + ".c2")

    c1.write("START")
    c2.write("START")

    rc1 = c1.read()
    rc2 = c2.read()

    s.write("+STARTED C1")
    s.write("+STARTED C2")

    r3 = s.read()
    r4 = s.read()

    assert(rc1 == "START")
    assert(rc2 == "START")
    assert(r3 == "+STARTED C1")
    assert(r4 == "+STARTED C2")

if __name__ == '__main__':
    test_Redis()
    test_ChannelList()
    #test ChannelRedis()
