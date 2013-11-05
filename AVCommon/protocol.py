import logging
import copy
import threading
from AVAgent import conf

from command import Command
from mq import MQStar


class ProtocolClient:
    """ Protocol, client side. When the command is received, it's executed and the result resent to the server. """

    def __init__(self, mq, client):
        self.mq = mq
        self.client = client

        assert(isinstance(client, str))
        assert(isinstance(mq, MQStar))

    def _execute_command(self, cmd):
        try:
            ret = cmd.execute(cmd.payload)
            if conf.verbose:
                logging.debug("cmd.execute ret: %s" % str(ret))
            cmd.success, cmd.payload = ret
        except Exception, e:
            logging.error("ERROR: %s %s " % (type(e), e))
            cmd.success = False
            cmd.payload = e

        assert isinstance(cmd.success, bool)
        self.send_answer(cmd)
        return cmd

    """ client side """
    def receive_command(self):
        assert(isinstance(self.client, str))
        #logging.debug("PROTO receiveCommand %s" % (self.client))
        msg = self.mq.receive_client(self.client, blocking=True, timeout=0)
        if conf.verbose:
            logging.debug("PROTO C receive_command %s, %s" % (self.client, msg))
        cmd = Command.unserialize(msg)
        cmd.vm = self.client

        return self._execute_command(cmd)

    def send_answer(self, reply):
        if conf.verbose:
            logging.debug("PROTO C send_answer %s" % reply)
        self.mq.send_server(self.client, reply.serialize())


class Protocol(ProtocolClient):
    """ A protocol implements the server behavior."""
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
        #logging.debug("PROTO S executing server")
        t = threading.Thread(target=self._execute_command, args=(cmd,))
        t.start()

        if blocking:
            t.join()

    def _meta(self, cmd):
        if conf.verbose:
            logging.debug("PROTO S executing meta")
        ret = cmd.execute( (self, cmd.payload) )

    #def next(self):
    #    logging.debug("next")
    #    for c in self.procedure.next():
    #        logging.debug("next, got a new command")
    #        yield self.send_command(c)

    def send_next_command(self):
        if not self.procedure:
            self.last_command = None
            return False
        self.last_command = self.procedure.next_command()
        self.send_command(self.last_command)
        return True

    def send_command(self, command):
        if conf.verbose:
            logging.debug("PROTO S send_command: %s" % str(command))
        cmd = Command.unserialize(command)
        cmd.vm = self.client
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
        cmd.vm = client
        if conf.verbose:
            logging.debug("PROTO S manage_answer %s: %s" % (client, cmd))

        assert(cmd.success is not None)
        cmd.on_answer(cmd.success, cmd.payload)

        return cmd
