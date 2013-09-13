import os
from redis import Redis, StrictRedis
from redis.exceptions import ConnectionError
import thread
import time


class Communicator:
    def write(self, message):
        pass

    def read(self):
        pass


class CommunicatorRedisList(Communicator):
    def __init__(self, host, channel):
        self.host = host
        self.channel = channel
        self.redis = StrictRedis(host, socket_timeout=60)
        print "  DBG init %s %s" % (host, channel)

    def write(self, message):
        print "  DBG publish %s" % message
        self.redis.rpush(self.channel, message)

    def read(self):
        value = self.redis.lpop(self.channel)

        print "  DBG received: %s" % value
        return value

class CommunicatorRedisPubSub(Communicator):
    def __init__(self, host, channel):
        self.host = host
        self.channel = channel
        self.redis = StrictRedis(host, socket_timeout=60)
        print "  DBG init %s %s" % (host, channel)

    def write(self, message):
        print "  DBG publish %s" % message
        self.redis.publish(self.channel, message)

    def close(self):
        print "  DBG close"
        self.redis.publish(self.channel, "+CLOSE")

    def read(self):
        p = self.redis.pubsub()
        if self.channel[-1] == "*":
            p.psubscribe(self.channel)
        else:
            p.subscribe(self.channel)
        for m in p.listen():
            print "  DBG received: %s" % m
            if m['type'].endswith("message"):
                if m['data'] == "+CLOSE":
                    break
                print "  DBG string: %s" % m['data']
                yield [m['channel'], m['data']]
