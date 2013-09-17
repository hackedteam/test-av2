
from redis import StrictRedis
import ast


class Channel():
    redis = None

    def __init__(self, host, channel):
        self.host = host
        self.channel = channel
        self.redis = StrictRedis(host, socket_timeout=60)
        print "  DBG init %s %s" % (host, channel)

    def write(self, message):
        print "  DBG write: %s\n    type: %s" % (str(message), type(message))
        if not self.redis.exists(self.channel):
            print "  DBG write, create new channel %s" % self.channel
        self.redis.rpush(self.channel, message)

    def read(self, blocking=False):
        if blocking:
            message = self.redis.blpop(self.channel)
        else:
            message = self.redis.lpop(self.channel)

        print "  DBG read: %s" % message
        try:
            parsed = ast.literal_eval(message)
        except:
            parsed = message

        print "      type: %s" % type(parsed)
        return parsed

