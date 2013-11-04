import logging
from redis import StrictRedis


class Channel():
    """ Communication Channel, via Redis
    A channel is defined by a (blocking) list on a redis server. Messages are strings. """
    redis = None

    def __init__(self, host, channel):
        """ A channel is defined by a redis host and a channel name
        """
        self.host = host
        self.channel = channel
        self.redis = StrictRedis(host, socket_timeout=60)
        logging.debug("  CH init %s %s" % (host, channel))
        if not self.redis.exists(self.channel):
            logging.debug("  CH write, new channel %s" % self.channel)

    def write(self, message):
        """ writes a message to the channel. The channel is created automatically """
        logging.debug("  CH write: %s\n    type: %s" % (str(message), type(message)))
        self.redis.rpush(self.channel, message)

    def read(self, blocking=False, timout=0):
        """ reads a message from the underlining channel. This method can be blocking or it could timeout in a while
        """
        if blocking:
            try:
                ch, message = self.redis.blpop(self.channel, timout)
            except:
                logging.debug("  CH timeout: %s" % str(self.channel))
                message = None
        else:
            message = self.redis.lpop(self.channel)

        logging.debug("  CH read: %s" % str(message))
        parsed = message

        logging.debug("      type: %s" % type(parsed))
        return parsed

