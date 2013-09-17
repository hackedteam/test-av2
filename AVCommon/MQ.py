import string
import random
from Channel import Channel


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


class MQStar():
    session = ""
    channels = {}
    """MQStar is a MessageQueue with a star topology based on Redis"""
    def __init__(self, host):
        self.host = host
        self.session = id_generator()
        channelServer = "MQ_%s_to_server" % self.session
        self.channelToServer = Channel(self.host, channelServer)

    def _makeChannel(self, frm="server", to="server"):
        name = "%s_%s_%s" % (self.session, frm, to)
        channel = Channel(self.host, name)
        return channel

    def clean(self):
        for k in self.channelToServer.redis.keys("MQ_*"):
            print "DBG clean %s" % k
            self.channelToServer.redis.delete(k)

    def addClient(self, client):
        if client not in self.channels.keys():
            ch = self._makeChannel(to=client)
            #chRight = self.channelToServer
            self.channels[client] = ch

    def addClients(self, clients):
        for c in clients:
            self.addClient(c)

    def sendToServer(self, client, message):
        if client not in self.channels.keys():
            print "DBG error, client not found"
        ch = self.channelToServer
        payload = (client, message)
        ch.write(payload)

    def serverRead(self):
        payload = self.channelToServer.read()
        print "DBG read: %s\n    type: %s" % (str(payload), type(payload))
        client, message = payload
        return payload

    def sendToClient(self,  client, message, frm="server",):
        if client not in self.channels.keys():
            print "DBG error, client not found"
        ch = self.channels[client]
        payload = frm, message
        ch.write(payload)

    def clientRead(self, client):
        if client not in self.channels.keys():
            print "DBG error, client not found"
        ch = self.channels[client]
        payload = ch.read()
        server, message = payload
        assert(server == "server")
        return message
 
