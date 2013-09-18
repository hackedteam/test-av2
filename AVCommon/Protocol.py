from Command import Command
from MQ import MQStar


class Protocol:
    commands = []

    def __init__(self, mq, client, commands=[]):
        self.mq = mq
        self.client = client
        self.commands = commands

        assert(isinstance(client, str))
        assert(isinstance(mq, MQStar))

    """server side"""
    def _sendCommand(self, cmd):
        cmd.onInit()
        self.mq.sendClient(self.client, cmd.serialize())

    def sendNextCommand(self):
        #print self.commands
        c = self.commands.pop(0)
        print "PROTO S sendNextCommand: %s" % str(c)
        cmd = Command.unserialize(c)
        self._sendCommand(cmd)

    """ client side """
    def receiveCommand(self):
        assert(isinstance(self.client, str))
        #print "PROTO receiveCommand %s" % (self.client)
        msg = self.mq.receiveClient(self.client)
        print "PROTO C receiveCommand %s, %s" % (self.client, msg)
        cmd = Command.unserialize(msg)
        
        cmd.answer = cmd.Execute()
        self.answerCommand(cmd)
        return msg

    """ client side """
    def answerCommand(self, reply):
        print "PROTO C answerCommand ", reply
        self.mq.sendServer(self.client, reply.serialize())

    """ server side """
    def receiveAnswer(self, client, msg):
        #msg = self.mq.receiveClient(self, client)

        cmd = Command.unserialize(msg)
        print "PROTO S receiveAnswer %s: %s" % (client, cmd)

        return cmd
