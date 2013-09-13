from communicator import CommunicatorRedisList, CommunicatorRedisPubSub
import time
import thread

"""
execute via py.test
"""

count = 0

def server(s):
    global count
    for c, m in s.read():
        print "RECEIVED: %s | %s" % (c, m)
        count += 1

def test_CommunicatorRedis():
    global count
    channel = "response"
    host = "localhost"

    s = CommunicatorRedisPubSub(host, channel + "*")
    c1 = CommunicatorRedisPubSub(host, channel + ".c1")
    c2 = CommunicatorRedisPubSub(host, channel + ".c2")

    try:
        thread.start_new_thread(server, (s, ))
        time.sleep(1)
        thread.start_new_thread(c1.write, ("Thread-1", ))
        thread.start_new_thread(c2.write, ("Thread-2", ))
        #thread.start_new_thread(sleep_and_close, (c2, ))
    except Exception, e:
        print "Error: unable to start thread %s" % e

    time.sleep(3)
    c1.close()
    assert count == 2

def test_CommunicatorList():
    global count
    channel = "response"
    host = "localhost"

    s = CommunicatorRedisList(host, channel)
    c1 = CommunicatorRedisList(host, channel + ".c1")
    c2 = CommunicatorRedisList(host, channel + ".c2")

    c1.write("START")
    c2.write("START")

    c1.read()
    c2.read()

    s.write("+STARTED C1")
    s.write("+STARTED C2")

    s.read()
    s.read()

if __name__ == '__main__':
    test_CommunicatorList()
    #test_CommunicatorRedis()
