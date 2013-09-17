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
        channelServer = "%s_to_server" % self.session
        self.channelToServer = Channel(self.host, channelServer)

    def _makeChannel(self, frm="server", to="server"):
        name = "%s_%s_%s" % (self.session, frm, to)
        channel = Channel(self.host, name)
        return channel

    def addClient(self, client):
        if client not in self.channels.keys():
            ch = self._makeChannel(session=self.session, to=client)
            #chRight = self.channelToServer
            self.channels[client] = ch

    def addClients(self, clients):
        for c in clients:
            self.addClient(c)

    def sendToServer(self, client, message):
        if client not in self.channels.keys():
            print "DBG error, client not found"
        ch = self.channelToServer
        ch.write([client, message])

    def serverRead(self):
        client, message = self.channelServer.read()
        return (client, message)

    def sendToClient(self, client, message):
        if client not in self.channels.keys():
            print "DBG error, client not found"
        ch = self.channel[client]
        ch.write(message)

    def clientRead(self, client):
        if client not in self.channels.keys():
            print "DBG error, client not found"
        ch = self.channel[client]
        message = ch.read()
        return message
 
