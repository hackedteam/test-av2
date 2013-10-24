import logging
from redis import StrictRedis


class Channel():
    redis = None

    def __init__(self, host, channel):
        self.host = host
        self.channel = channel
        self.redis = StrictRedis(host, socket_timeout=60)
        logging.debug("  CH init %s %s" % (host, channel))
        if not self.redis.exists(self.channel):
            logging.debug("  CH write, new channel %s" % self.channel)

    def write(self, message):
        logging.debug("  CH write: %s\n    type: %s" % (str(message), type(message)))
        self.redis.rpush(self.channel, message)

    def read(self, blocking=False, timout=0):
        if blocking:
            try:
                ch, message = self.redis.blpop(self.channel, timout)
            except:
                logging.debug("  CH timeout: %s" % str(self.channel))
                message = None
        else:
            message = self.redis.lpop(self.channel)

        logging.debug("  CH read: %s" % str(message))
        #try:
        #parsed = ast.literal_eval(message)
        #parsed = tuple(message[1:-1].split(", ", 1))
        #b = re.compile("\('(\w+)'")
        #except:
        parsed = message

        logging.debug("      type: %s" % type(parsed))
        return parsed

