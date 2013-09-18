import string
import random
from Channel import Channel


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


class MQStar():
    session = ""
    channels = {}
    """MQStar is a MessageQueue with a star topology based on Redis"""
    def __init__(self, host, session=None):
        self.host = host
        if not session:
            self.session = id_generator()
        else:
            self.session = session

        channelServer = " MQ_%s_to_server" % self.session
        self.channelToServer = Channel(self.host, channelServer)

    def _makeChannel(self, frm="server", to="server"):
        name = "%s_%s_%s" % (self.session, frm, to)
        channel = Channel(self.host, name)
        return channel

    def clean(self):
        for k in self.channelToServer.redis.keys("MQ_*"):
            print " MQ clean %s" % k
            self.channelToServer.redis.delete(k)

    def addClient(self, client):
        if client not in self.channels.keys():
            ch = self._makeChannel(to=client)
            #chRight = self.channelToServer
            self.channels[client] = ch

    def addClients(self, clients):
        for c in clients:
            self.addClient(c)

    def sendServer(self, client, message):
        if client not in self.channels.keys():
            print " MQ error, client not found"
        ch = self.channelToServer
        payload = (client, message)
        ch.write(payload)

    def receiveServer(self, blocking=False, timeout=60):
        payload = self.channelToServer.read(blocking, timeout)
        print " MQ read: %s\n    type: %s" % (str(payload), type(payload))
        #client, message = payload
        return payload

    def sendClient(self,  client, message):
        if client not in self.channels.keys():
            print " MQ error, sendClient, client not found: %s" % self.channels
        ch = self.channels[client]
        ch.write(message)

    def receiveClient(self, client, blocking=False, timeout=60):
        assert(isinstance(client, str))
        if client not in self.channels.keys():
            print " MQ error, receiveClient, client (%s) not found: %s" % (client, self.channels)
        ch = self.channels[client]
        message = ch.read(blocking, timeout)
        return message
 
