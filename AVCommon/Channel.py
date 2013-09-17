import os
from redis import Redis, StrictRedis
from redis.exceptions import ConnectionError
import thread
import time


class Channel():
    def __init__(self, host, channel):
        self.host = host
        self.channel = channel
        self.redis = StrictRedis(host, socket_timeout=60)
        print "  DBG init %s %s" % (host, channel)

    def write(self, message):
        print "  DBG write %s" % message
        if not self.redis.exists(self.channel):
            print "  DBG write, creade new channel %s" % self.channel            
        self.redis.rpush(self.channel, message)

    def read(self, blocking=False):
        if blocking:
            value = self.redis.blpop(self.channel)
        else:
            value = self.redis.lpop(self.channel)

        print "  DBG received: %s" % value
        return value

