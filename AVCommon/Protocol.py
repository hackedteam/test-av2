from Command import Command
from MQ import MQStar
import logging
import copy

class ProtocolClient:
    def __init__(self, mq, client):
        self.mq = mq
        self.client = client

        assert(isinstance(client, str))
        assert(isinstance(mq, MQStar))

    def _executeCommand(self, cmd):
        try:
            ret = cmd.Execute(cmd.payload)
            cmd.success, cmd.payload = ret
        except Exception, e:
            cmd.success = False
            cmd.payload = e

        assert isinstance(cmd.success, bool)
        self.sendAnswer(cmd)
        return cmd

    """ client side """
    def receiveCommand(self):
        assert(isinstance(self.client, str))
        #logging.debug("PROTO receiveCommand %s" % (self.client))
        msg = self.mq.receiveClient(self.client, blocking=True, timeout=5)
        logging.debug("PROTO C receiveCommand %s, %s" % (self.client, msg))
        cmd = Command.unserialize(msg)

        return self._executeCommand(cmd)

    def sendAnswer(self, reply):
        logging.debug("PROTO C sendAnswer %s" % reply)
        self.mq.sendServer(self.client, reply.serialize())


class Protocol(ProtocolClient):
    procedure = None

    def __init__(self, mq, client, procedure=None):
        self.mq = mq
        self.client = client
        self.procedure = copy.deepcopy(procedure)

        assert(isinstance(client, str))
        assert(isinstance(mq, MQStar))

    """server side"""
    def _sendCommand(self, cmd):
        cmd.onInit(cmd.payload)
        self.mq.sendClient(self.client, cmd.serialize())

    def _execute(self, cmd, blocking=False):
        logging.debug("PROTO S executing server")
        t = threading.Thread(self._executeCommand, ())
        t.start()

        if blocking:
            t.join()

    def sendNextCommand(self):
        if not self.procedure:
            return False
        c = self.procedure.nextCommand()
        self.sendCommand(c)

    def sendCommand(self, command):
        logging.debug("PROTO S sendCommand: %s" % str(command))
        cmd = Command.unserialize(command)

        if cmd.side == "client":
            self._sendCommand(cmd)
        else:
            self._execute(cmd)
        return True

    def receiveAnswer(self, client, msg):
        #msg = self.mq.receiveClient(self, client)

        cmd = Command.unserialize(msg)
        logging.debug("PROTO S receiveAnswer %s: %s" % (client, cmd))

        assert(cmd.success is not None)
        cmd.onAnswer(cmd.success, cmd.payload)

        return cmd
