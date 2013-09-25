import sys, os
import inspect
import logging
import abc
import ast
from Decorators import returns

def init_commands():
    logging.debug("initCommands")
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.append(cwd)
    for m in Command.commands:
        try:
            Command.known_commands[m] = __import__("Command_%s" % m)
        except:  # pragma: no cover
            import AVCommon
            Command.known_commands[m] = __import__("AVCommon.Command_%s" % m)
    #logging.debug("dir(): %s %s" % (dir(), dir("AVCommon")) )
    logging.info("Commands: %s" % Command.known_commands.keys())
    return True

class Command():
    __metaclass__ = abc.ABCMeta

    commands = ["START", "STARTVM", "STOPVM", "REVERT", "UPDATE", "PULL", "PUSH",
        "EXECUTE_VM", "SCREENSHOT", "START_AGENT", "SET_SERVER", "SET_PARAMS",
        "SET_BLACKLIST", "BUILD", "EXECUTE_AGENT", "UPGRADE_ELITE", "CHECK_STATIC",
        "PROCEDURE", "END", "EVAL_SERVER", "EVAL_CLIENT"]
    # STARTVM STOPVM REVERT UPDATE PULL PUSH EXECUTE_VM SCREENSHOT START_AGENT SET_SERVER SET_PARAMS SET_BLACKLIST BUILD EXECUTE_AGENT UPGRADE_ELITE CHECK_STATIC PROCEDURE END
    known_commands = dict(zip(commands,  [None] * len(commands)))

    payload = ""
    success = None
    context = None

    init = False;

    """command"""
    def __init__(self, name):
        self.name = name
        if not Command.init:
            Command.init = init_commands()
        assert(len(Command.known_commands) > 0)

    @staticmethod
    def unserialize(serialized):
        if not Command.init:
            Command.init = init_commands()

        #ident, command, answer = serialized.split(',', 2)
        #assert(ident == "CMD")
        success = None
        payload = None

        assert serialized, "cannot unserialize a null argument"
        if isinstance(serialized, Command):
            return serialized
        elif isinstance(serialized, dict):
            assert len(serialized)==1
            command = serialized.keys()[0]
            payload = serialized[command]
        elif len(serialized) == 3:
            command, success, payload = serialized
        elif len(serialized) == 2:
            command, payload = serialized
        else:
            command = serialized

        className = "Command_%s" % command
        #print Command.knownCommands
        assert(isinstance(success, bool) or success is None)
        assert isinstance(command, str), "not a string: %s" % command
        assert command in Command.known_commands.keys(), "Unknown command: %s" % command

        #logging.debug("dir: ", dir(Command.knownCommands[command]))
        if command in Command.known_commands.keys():
            m = Command.known_commands[command]
            c = getattr(m, className)
            #print sys.path
            cmd = c(command)
            #print c

            if payload.startswith("*"):
                cmd.payload = payload[1:]
            else:
                try:
                    cmd.payload = ast.literal_eval(payload)
                except:
                    cmd.payload = payload
            cmd.success = success
            return cmd

    def serialize(self):
        return (self.name, self.success, self.payload)

    """ server side """
    @abc.abstractmethod
    def on_init(self, args):
        pass  # pragma: no cover

    @abc.abstractmethod
    def on_answer(self, success, answer):
        pass  # pragma: no cover

    """ client side """
    @abc.abstractmethod
    def execute(self, args):
        pass  # pragma: no cover

    def __str__(self):
        return "%s,%s,%s" % (self.name, self.success, self.payload)


class ServerCommand(Command):
    side = "server"
    def on_init(self, args):
        pass  # pragma: no cover

    def on_answer(self, success, answer):
        pass  # pragma: no cover


class ClientCommand(Command):
    side = "client"
