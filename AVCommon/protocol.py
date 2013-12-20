from AVCommon.logger import logging
import copy
import threading
from AVCommon import config

import command
from mq import MQStar

import traceback


class ProtocolClient:
    """ Protocol, client side. When the command is received, it's executed and the result resent to the server. """

    def __init__(self, mq, vm, timeout=0):
        self.mq = mq
        self.vm = vm
        self.timeout = 0
        self.on_error = "SKIP" # ["SKIP", "CONTINUE", "STOP"]

        assert (isinstance(vm, str))
        assert mq

    def _execute_command(self, cmd):
        try:
            ret = cmd.execute(self.vm, cmd.args)
            logging.debug("cmd.execute ret: %s" % str(ret))
            cmd.success, cmd.result = ret
        except Exception, e:
            logging.exception("ERROR:_execute_command")
            cmd.success = False
            cmd.result = e

        assert isinstance(cmd.success, bool)
        self.send_answer(cmd)
        return cmd


    def _meta(self, cmd):
        if config.verbose:
            logging.debug("PROTO S executing meta")
        ret = cmd.execute(self.vm, self, cmd.args)
        cmd.success, cmd.result = ret
        assert isinstance(cmd.success, bool)
        self.send_answer(cmd)
        return cmd

    # client side
    def receive_command(self):
        assert (isinstance(self.vm, str))
        #logging.debug("PROTO receiveCommand %s" % (self.client))
        msg = self.mq.receive_client(self.vm, blocking=True, timeout=self.timeout)
        if config.verbose:
            logging.debug("PROTO C receive_command %s, %s" % (self.vm, msg))
        cmd = command.unserialize(msg)
        cmd.vm = self.vm

        if cmd.side == "meta":
            return self._meta(cmd)
        else:
            return self._execute_command(cmd)

    def send_answer(self, reply):
        if config.verbose:
            logging.debug("PROTO C send_answer %s" % reply)
        self.mq.send_server(self.vm, reply.serialize())


class Protocol(ProtocolClient):
    """ A protocol implements the server behavior."""
    procedure = None
    last_command = None

    def __init__(self, dispatcher, vm, procedure=None, timeout=0):
        ProtocolClient.__init__(self, dispatcher.mq, vm, timeout)
        self.dispatcher = dispatcher
        self.vm = vm
        self.procedure = copy.deepcopy(procedure)
        self.sent_commands = []
        assert (isinstance(vm, str))
        assert dispatcher
        self.add_vm(vm)

    def add_vm(self, vm):
        self.mq.add_client(vm)

    # server side
    def _send_command_mq(self, cmd):
        accept = cmd.on_init(self, cmd.args)
        if accept == True:
            if config.verbose:
                logging.debug("sending command to client")
            self.mq.send_client(self.vm, cmd.serialize())
        elif accept == None:
            logging.debug("don't send command to client")
            cmd.success = True
            cmd.result = "blocked by on_init"
            self.send_answer(cmd)
        else:
            logging.debug("error sending command to client")
            cmd.success = False
            cmd.result = "blocked by on_init with error"
            self.send_answer(cmd)

    def _execute_command_server(self, cmd):
        try:
            ret = cmd.execute(self.vm, self, cmd.args)
            logging.debug("cmd.execute ret: %s" % str(ret))
            cmd.success, cmd.result = ret
        except Exception, e:
            logging.exception("ERROR:_execute_command")
            cmd.success = False
            cmd.result = e

        assert isinstance(cmd.success, bool)
        self.send_answer(cmd)
        return cmd

    def _execute(self, cmd, blocking=False):
        #logging.debug("PROTO S executing server")
        t = threading.Thread(target=self._execute_command_server, args=(cmd,))
        t.start()

        if blocking:
            t.join()

    def send_next_call(self):
        while(True):
            if not self.procedure:
                self.last_command = None
                return False

            self.last_command = self.procedure.next_command()
            name = self.last_command.name
            if name == "CALL":
                break
            if name.startswith("STOP") or name.startswith("REPORT"):
                break
            logging.debug("skipping to the next: %s" % self.last_command.name)

        #return self.send_command(copy.deepcopy(self.last_command))
        return self.send_command(self.last_command)

    def send_next_command(self):
        if not self.procedure:
            self.last_command = None
            return False
        self.last_command = self.procedure.next_command()
        #return self.send_command(copy.deepcopy(self.last_command))
        return self.send_command(self.last_command)

    def send_command(self, cmd):
        self.sent_commands.append(cmd)
        if config.verbose:
            logging.debug("PROTO S send_command: %s" % str(cmd))
            #cmd = command.unserialize(cmd)

        cmd.reset(self.vm)

        try:
            if cmd.side == "client":
                self._send_command_mq(cmd)
            elif cmd.side == "server":
                self._execute(cmd)
            elif cmd.side == "meta":
                self._meta(cmd)
            return True
        except Exception, ex:
            cmd.success = False
            cmd.result = str(ex)
            logging.exception("Error sending command %s: %s" % (cmd, ex))

            return False

    def receive_answer(self, vm, cmd):
        """ returns a command with name, success and payload """
        #msg = self.mq.receiveClient(self, client)

        sent_command = self.sent_commands[0]

        cmd.reset(vm)

        if config.verbose:
            logging.debug("PROTO S manage_answer %s: %s" % (vm, cmd))

        if cmd.success != None and cmd.name == sent_command.name:
            if config.verbose:
                logging.debug("PROTO S we got the expected answer")
            cmd.on_answer(vm, cmd.success, cmd.result)
            self.sent_commands.pop(0)
        else:
            if config.verbose:
                logging.debug("PROTO S ignoring unexpected answer: ")
                #logging.debug("cmd.timestamp == sent_command.timestamp: %s" % cmd.timestamp == sent_command.timestamp)
            cmd.success = None

        return cmd