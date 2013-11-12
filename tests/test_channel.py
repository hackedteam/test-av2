from unittest import TestCase
import os
import sys
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import time
import thread
from redis import StrictRedis
import ast
import string
import random
import logging, sys
import logging.config

import unittest

from AVCommon.channel import Channel

__author__ = 'zeno'

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def binary_generator(size=6, chars=range(256)):
    return ''.join(chr(random.choice(chars)) for x in range(size))

def server(s):
    global count
    for c, m in s.read():
        print "RECEIVED: %s | %s" % (c, m)
        count += 1

#
class TestChannel(unittest.TestCase):


    def test_Redis(self):
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

    def test_ChannelTimeout(self):
        channel = "test"
        host = "localhost"
        s = Channel(host, channel)
        r = s.read(blocking=True, timeout=1)
        assert r is None

    def test_ChannelList(self):
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

        assert rc1 == "START", "not a START: %s" % rc1
        assert(rc2 == "START")
        assert(r3 == "+STARTED C1")
        assert(r4 == "+STARTED C2")



    def test_ChannelRandom(self):
        global count
        channel = id_generator()
        host = "localhost"

        s = Channel(host, channel)
        c1 = Channel(host, channel + ".c1")

        messages = [ id_generator(size=1000) for i in range(10)]

        for m in messages:
            c1.write(m)

        for m in messages:
            r = c1.read()
            assert(m == r)

    def test_ChannelBinary(self):
        global count
        channel = id_generator()
        host = "localhost"

        s = Channel(host, channel)
        c1 = Channel(host, channel + ".c1")

        messages = [ binary_generator(size=100) for i in range(10)]

        for m in messages:
            c1.write(m)

        for m in messages:
            r = c1.read()
            assert(m == r)

if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')

    #test_dispatcher_server()
    unittest.main()