import sys
import os
import logging
import ast
import re
import abc


def init_commands():
    logging.debug("initCommands")
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.append(cwd)
    for m in Command.commands:
        #try:
        #Command.known_commands[m] = __import__("Command_%s" % m)
        Command.known_commands[m] = __import__("AVCommon.Command_%s" % m)
        #except:  # pragma: no cover
        #    raise
        #    import AVCommon
        #    Command.known_commands[m] = __import__("AVCommon.Command_%s" % m)
    #logging.debug("dir(): %s %s" % (dir(), dir("AVCommon")) )
    logging.info("Commands: %s" % Command.known_commands.keys())
    return True


class Command(object):
    __metaclass__ = abc.ABCMeta

    commands = ["BEGIN", "START_VM", "STOP_VM", "REVERT", "UPDATE", "PULL", "PUSH",
        "EXECUTE_VM", "SCREENSHOT", "COMMAND_CLIENT", "START_AGENT", "STOP_AGENT",
        "CALL", "END", "EVAL_SERVER", "EVAL_CLIENT"]
    # START_VM STOP_VM REVERT UPDATE PULL PUSH EXECUTE_VM SCREENSHOT START_AGENT SET_SERVER SET_PARAMS SET_BLACKLIST BUILD EXECUTE_AGENT UPGRADE_ELITE CHECK_STATIC PROCEDURE END
    known_commands = dict(zip(commands,  [None] * len(commands)))

    payload = ""
    success = None
    context = None
    init = False

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
        cmd = serialized
        success = None
        payload = None

        assert serialized, "cannot unserialize a null argument"

        if isinstance(serialized, Command):
            return serialized
        elif isinstance(serialized, dict):
            assert len(serialized)==1
            cmd = serialized.keys()[0]
            payload = serialized[cmd]
        elif len(serialized) == 3:
            cmd, success, payload = serialized
        elif len(serialized) == 2:
            cmd, payload = serialized
        elif isinstance(serialized, str):
            #TODO: add ast.literal_eval di ('START', None, None)
            m = re.compile("\('(\w+)\', (\w+), (.+)\)").match(serialized)
            if m:
                groups = m.groups()
                assert len(groups) == 3
                cmd = groups[0]
                success = ast.literal_eval(groups[1])
                try:
                    payload = ast.literal_eval(groups[2])
                except SyntaxError:
                    payload = groups[2]

        class_name = "Command_%s" % cmd
        #print Command.knownCommands
        assert(isinstance(success, bool) or success is None)
        assert isinstance(cmd, str), "not a string: %s" % cmd
        assert cmd in Command.known_commands.keys(), "Unknown command: %s" % cmd

        if cmd in Command.known_commands.keys():
            m = Command.known_commands[cmd]

            #logging.debug("m: %s", m)
            #logging.debug("dir: %s", dir(Command.known_commands[cmd]))

            command_package = getattr(m, class_name)
            command_class = getattr(command_package, class_name)
            #command_class = getattr(m, class_name)
            #logging.debug("command_class: %s", command_class)
            #print sys.path
            c = command_class(cmd)
            #print c

            if isinstance(payload, str) and payload.startswith("*"):
                c.payload = payload[1:]
            else:
                try:
                    c.payload = ast.literal_eval(payload)
                except:
                    c.payload = payload
            c.success = success
            c.context = Command.context

            assert isinstance(c, Command), "not an instance: %s of %s" % (c.__class__, Command)
            return c

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

class MetaCommand(Command):
    side = "meta"
    def on_init(self, args):
        pass  # pragma: no cover

    def on_answer(self, success, answer):
        pass  # pragma: no cover
