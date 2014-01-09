from AVCommon.logger import logging
from redis import StrictRedis
from AVCommon import config
from redis.exceptions import ConnectionError
import time

class Channel():
    """ Communication Channel, via Redis
    A channel is defined by a (blocking) list on a redis server. Messages are strings. """
    redis = None

    def __init__(self, host, channel):
        """ A channel is defined by a redis host and a channel name
        """
        self.host = host
        self.channel = channel
        self.redis = StrictRedis(host, socket_timeout=None)
        #logging.debug("  CH init %s %s" % (host, channel))
        if not self.redis.exists(self.channel):
            if config.verbose:
                logging.debug("  CH write, new channel %s" % self.channel)

    def write(self, message):
        """ writes a message to the channel. The channel is created automatically """
        if config.verbose:
            logging.debug("  CH write: channel: %s  message: %s" % (str(self.channel), str(message)))

        while(True):
            pipe = self.redis.pipeline()
            l1,ret,l2 = pipe.llen(self.channel).rpush(self.channel, message).llen(self.channel).execute()
            if not ret:
                logging.error("not ret: %s" % self.channel)
                continue
            if not l2>0:
                logging.error("not l2>0 %s" % self.channel)
                continue
            if l1 and not l2 == l1 +1:
                logging.error("l1 and not l2 == l1 +1: %s" % self.channel)
                continue
            break

    def read(self, blocking=False, timeout=0):
        """ reads a message from the underlining channel. This method can be blocking or it could timeout in a while
        """
        ret = None
        time_start = time.time()
        if blocking:
            while True:
                try:
                    pipe = self.redis.pipeline()
                    retup = pipe.llen(self.channel).blpop(self.channel, timeout).llen(self.channel).execute()
                    l1,ret,l2 = retup

                    if ret == None:
                        if config.verbose:
                            logging.debug("None in blpop: %s" % self.channel)

                        if timeout and (time.time() - time_start) > timeout:
                            logging.exception("  CH TIMEOUT server explicit")
                            return None
                        time.sleep(5)

                        continue
                    else:
                        assert l1>=0
                        assert l2>=0
                        assert l1 == l2 + 1, "l1: %s l2: %s" %(l1,l2)

                    break;
                except ConnectionError, e:
                    logging.exception("  CH TIMEOUT server")
                    ret = None

            if not ret and timeout:
                logging.debug("  CH TIMEOUT read")
                return None

            ch, message = ret

        else:
            message = self.redis.lpop(self.channel)

        #logging.debug("  CH read: %s" % str(message))
        parsed = message

        #logging.debug("      type: %s" % type(parsed))
        return parsed

