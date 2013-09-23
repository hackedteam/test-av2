import sys, os
import inspect
import logging
import abc
import ast
from Decorators import returns

def initCommands():
    logging.debug("initCommands")
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.append(cwd)
    for m in Command.commands:
        try:
            Command.knownCommands[m] = __import__("Command_%s" % m)
        except:  # pragma: no cover
            import AVCommon
            Command.knownCommands[m] = __import__("AVCommon.Command_%s" % m)
    #logging.debug("dir(): %s %s" % (dir(), dir("AVCommon")) )
    logging.info("Commands: %s" % Command.knownCommands.keys())
    return True

class Command():
    __metaclass__ = abc.ABCMeta

    commands = ["START", "STARTVM", "STOPVM", "REVERT", "UPDATE", "PULL", "PUSH",
        "EXECUTE_VM", "SCREENSHOT", "START_AGENT", "SET_SERVER", "SET_PARAMS",
        "SET_BLACKLIST", "BUILD", "EXECUTE_AGENT", "UPGRADE_ELITE", "CHECK_STATIC",
        "PROCEDURE", "END"]
    # STARTVM STOPVM REVERT UPDATE PULL PUSH EXECUTE_VM SCREENSHOT START_AGENT SET_SERVER SET_PARAMS SET_BLACKLIST BUILD EXECUTE_AGENT UPGRADE_ELITE CHECK_STATIC PROCEDURE END
    knownCommands = dict(zip(commands,  [None] * len(commands)))

    payload = ""
    success = None
    context = None

    init = False;

    """command"""
    def __init__(self, name):
        self.name = name
        if not Command.init:
            Command.init = initCommands()
        assert(len(Command.knownCommands) > 0)

    @staticmethod
    def unserialize(serialized):
        if not Command.init:
            Command.init = initCommands()

        #ident, command, answer = serialized.split(',', 2)
        #assert(ident == "CMD")
        success = None
        payload = None

        if isinstance(serialized, dict):
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
        assert isinstance(command, str),"not a string: %s" % command
        #logging.debug("%s Command.knownCommands.keys: %s" % (command, Command.knownCommands.keys()))
        assert command in Command.knownCommands.keys(), "Unknown command: %s" % command

        #logging.debug("dir: ", dir(Command.knownCommands[command]))
        if command in Command.knownCommands.keys():
            m = Command.knownCommands[command]
            c = getattr(m, className)
            #print sys.path
            cmd = c(command)
            #print c

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
    def onInit(self, args):
        pass  # pragma: no cover

    @abc.abstractmethod
    def onAnswer(self, success, answer):
        pass  # pragma: no cover

    """ client side """
    @abc.abstractmethod
    def Execute(self, args):
        pass  # pragma: no cover

    def __str__(self):
        return "%s,%s,%s" % (self.name, self.success, self.payload)


class ServerCommand(Command):
    side = "server"
    def onInit(self, args):
        pass  # pragma: no cover

    def onAnswer(self, success, answer):
        pass  # pragma: no cover


class ClientCommand(Command):
    side = "client"
