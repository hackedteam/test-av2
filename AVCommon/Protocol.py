from Command import Command
from MQ import MQStar
import logging


class ProtocolClient:
    def __init__(self, mq, client):
        self.mq = mq
        self.client = client

        assert(isinstance(client, str))
        assert(isinstance(mq, MQStar))

    """ client side """
    def receiveCommand(self):
        assert(isinstance(self.client, str))
        #logging.debug("PROTO receiveCommand %s" % (self.client))
        msg = self.mq.receiveClient(self.client, blocking=True, timeout=5)
        logging.debug("PROTO C receiveCommand %s, %s" % (self.client, msg))
        cmd = Command.unserialize(msg)

        try:
            ret = cmd.Execute(cmd.payload)
            cmd.success, cmd.payload = ret
        except Exception, e:
            cmd.success = False
            cmd.payload = e

        assert isinstance(cmd.success, bool)
        self.sendAnswer(cmd)
        return cmd

    def sendAnswer(self, reply):
        logging.debug("PROTO C sendAnswer %s" % reply)
        self.mq.sendServer(self.client, reply.serialize())


class Protocol(ProtocolClient):
    commands = []

    def __init__(self, mq, client, commands=[]):
        self.mq = mq
        self.client = client
        self.commands = commands

        assert(isinstance(client, str))
        assert(isinstance(mq, MQStar))

    """server side"""
    def _sendCommand(self, cmd):
        cmd.onInit(cmd.payload)
        self.mq.sendClient(self.client, cmd.serialize())

    def sendNextCommand(self):
        #print self.commands
        if len(self.commands) == 0:
            return False
        c = self.commands.pop(0)
        logging.debug("PROTO S sendNextCommand: %s" % str(c))
        cmd = Command.unserialize(c)
        self._sendCommand(cmd)
        return True

    def sendCommand(self, command):
        logging.debug("PROTO S sendNextCommand: %s" % str(command))
        cmd = Command.unserialize(command)
        self._sendCommand(cmd)
        return True

    def receiveAnswer(self, client, msg):
        #msg = self.mq.receiveClient(self, client)

        cmd = Command.unserialize(msg)
        logging.debug("PROTO S receiveAnswer %s: %s" % (client, cmd))

        assert(cmd.success is not None)
        cmd.onAnswer(cmd.success, cmd.payload)

        return cmd
