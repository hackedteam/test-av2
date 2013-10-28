import logging
import copy
import threading

from command import Command
from mq import MQStar


class ProtocolClient:

    def __init__(self, mq, client):
        self.mq = mq
        self.client = client

        assert(isinstance(client, str))
        assert(isinstance(mq, MQStar))

    def _executeCommand(self, cmd):
        try:
            ret = cmd.execute(cmd.payload)
            logging.debug("cmd.execute: %s" % str(ret))
            cmd.success, cmd.payload = ret
        except Exception, e:
            logging.error(e)
            cmd.success = False
            cmd.payload = e

        assert isinstance(cmd.success, bool)
        self.send_answer(cmd)
        return cmd

    """ client side """
    def receive_command(self):
        assert(isinstance(self.client, str))
        #logging.debug("PROTO receiveCommand %s" % (self.client))
        msg = self.mq.receive_client(self.client, blocking=True, timeout=5)
        logging.debug("PROTO C receiveCommand %s, %s" % (self.client, msg))
        cmd = Command.unserialize(msg)

        return self._executeCommand(cmd)

    def send_answer(self, reply):
        logging.debug("PROTO C sendAnswer %s" % reply)
        self.mq.send_server(self.client, reply.serialize())


class Protocol(ProtocolClient):
    procedure = None

    def __init__(self, mq, client, procedure=None):
        self.mq = mq
        self.client = client
        self.procedure = copy.deepcopy(procedure)

        assert(isinstance(client, str))
        assert(isinstance(mq, MQStar))

    """server side"""
    def _send_command_mq(self, cmd):
        cmd.on_init(cmd.payload)
        self.mq.send_client(self.client, cmd.serialize())

    def _execute(self, cmd, blocking=False):
        logging.debug("PROTO S executing server")
        t = threading.Thread(target=self._executeCommand, args=(cmd,))
        t.start()

        if blocking:
            t.join()

    def _meta(self, cmd):
        logging.debug("PROTO S executing meta")
        ret = cmd.execute( (self, cmd.payload) )

    #def next(self):
    #    logging.debug("next")
    #    for c in self.procedure.next():
    #        logging.debug("next, got a new command")
    #        yield self.send_command(c)

    def send_next_command(self):
        if not self.procedure:
            return False
        c = self.procedure.next_command()
        self.send_command(c)
        return True

    def send_command(self, command):
        logging.debug("PROTO S sendCommand: %s" % str(command))
        cmd = Command.unserialize(command)

        try:
            if cmd.side == "client":
                self._send_command_mq(cmd)
            elif cmd.side == "server":
                self._execute(cmd)
            elif cmd.side == "meta":
                self._meta(cmd)
            return True
        except Exception, ex:
            logging.error("Error sending command %s: %s" % (command, ex))
            return False

    def receive_answer(self, client, msg):
        """ returns a command with name, success and payload """
        #msg = self.mq.receiveClient(self, client)

        cmd = Command.unserialize(msg)
        logging.debug("PROTO S receiveAnswer %s: %s" % (client, cmd))

        assert(cmd.success is not None)
        cmd.on_answer(cmd.success, cmd.payload)

        return cmd
