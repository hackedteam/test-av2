import sys
import os
import logging
import ast
import re
import abc
from types import ModuleType
from AVCommon import config

server_commands = ['BEGIN',
 'CALL',
 'COMMAND_CLIENT',
 'END',
 'EVAL_CLIENT',
 'EVAL_SERVER',
 'EXECUTE_VM',
 'PULL',
 'PUSH',
 'REVERT',
 'SCREENSHOT',
 'START_AGENT',
 'START_VM',
 'STOP_AGENT',
 'STOP_VM',
 'UPDATE']

command_names = []
known_commands = {}

def init(namespace = "AVCommon", commands = server_commands, append = False):
    global command_names
    global known_commands
    #logging.debug("initCommands")

    #cwd = os.getcwd()
    #if cwd not in sys.path:
    #    sys.path.append(cwd)
    if not append:
        command_names = []
        #Command.known_commands = dict(zip(commands,  [None] * len(commands)))

    command_names = command_names + commands
    for m in commands:
        try:
            known_commands[m] = __import__("%s.Command_%s" % (namespace, m))
        except:
            known_commands[m] = __import__("Command_%s" % m)

        #    import AVCommon
        #    Command.known_commands[m] = __import__("AVCommon.Command_%s" % m)
    #logging.debug("dir(): %s %s" % (dir(), dir("AVCommon")) )

    #logging.info("Commands: %s" % known_commands.keys())


class Command(object):
    """ A Command is a base class for any instruction to give on a channel.
    A command is defined by a name and an implementation class. Each class can be Server, Client or Meta.

    """

    global command_names
    global known_commands

    __metaclass__ = abc.ABCMeta


    payload = ""
    success = None
    context = None
    vm = None

    def __init__(self, name):
        """ A command is constructed with a name, that identifies the derived class """
        self.name = name
        #assert len(known_commands) > 0, "empty known commands"
        #assert name in command_names, "name not in command_names: %s" % name

    @staticmethod
    def unserialize(serialized):
        """ a command cane be unserialized in many ways:
        - command instance
        - dict: { command: payload }
        - tuple/array: (cmd, success, payload) or (cmd, payload)
        - str: "(cmd, success, payload)"

        payload is evaluated via ast, so that it can contain a type like tuple, array, number, dict and so on
        if payload begins with a "|", it's considered a plain string and it's not evaluated
        """
        if not command_names:
            init()

        #ident, command, answer = serialized.split(',', 2)
        #assert(ident == "CMD")
        cmd = serialized
        success = None
        payload = None

        assert serialized, "cannot unserialize a null argument"

        identified = "instance"
        if isinstance(serialized, Command):
            return serialized
        elif isinstance(serialized, dict):
            identified = "dict"
            assert len(serialized)==1
            cmd = serialized.keys()[0]
            payload = serialized[cmd]
        elif not isinstance(serialized, str) and len(serialized) == 3:
            identified = "len 3"
            cmd, success, payload = serialized
        elif not isinstance(serialized, str) and len(serialized) == 2:
            identified = "len 2"
            cmd, payload = serialized
        elif isinstance(serialized, str):
            identified = "str"
            m = re.compile("\('(\w+)\', (\w+), (.+)\)").match(serialized)
            if m:
                identified = "re"
                groups = m.groups()
                assert len(groups) == 3
                cmd = groups[0]
                success = ast.literal_eval(groups[1])
                try:
                    payload = ast.literal_eval(groups[2])
                except SyntaxError:
                    payload = groups[2]
                except ValueError:
                    payload = groups[2]

        class_name = "Command_%s" % cmd
        #logging.debug(1)Command.knownCommands

        if config.verbose:
            logging.debug("identified: %s" % identified)
        assert isinstance(success, bool) or success is None, "success: %s" % success
        assert isinstance(cmd, str), "not a string: %s" % cmd
        assert cmd in known_commands.keys(), "Unknown command: %s" % cmd

        if cmd in known_commands.keys():
            m = known_commands[cmd]

            command_module = getattr(m, class_name)
            if  isinstance(command_module, ModuleType):
                #assert isinstance(command_module, ModuleType), "strange type: %s" % command_module
                command_class = getattr(command_module, class_name)
            else:
                command_class = command_module
            command_class.name = class_name
            c = command_class(cmd)

            if isinstance(payload, str) and payload.startswith("|"):
                c.payload = payload[1:]
            else:
                try:
                    c.payload = ast.literal_eval(payload)
                except:
                    c.payload = payload
            c.success = success
            c.context = Command.context

            #assert isinstance(c, Command), "not an instance: %s of %s" % (c.__class__, Command)
            return c

    def serialize(self):
        """ a command is serialiazed with a tuple: name, success and payload.
        name: the command name
        success: the success of the computation
        payload: the arguments or the result of the computation
        """
        return self.name, self.success, self.payload

    # server side
    def on_init(self, args):
        """ server side abstract method, is executed server side before the command is sent
        """
        pass  # pragma: no cover

    def on_answer(self, success, answer):
        """ server side abstract method, is executed server side when the result of the computation returns.
        """
        pass  # pragma: no cover

    # client side
    @abc.abstractmethod
    def execute(self, args):
        """ The computation itself
        """
        pass  # pragma: no cover

    def __str__(self):
        return "%s,%s,%s" % (self.name, self.success, self.payload)

class ServerCommand(Command):
    """ A ServerCommand is evaluated only server side, it's not sent to any client
    """
    side = "server"
    def on_init(self, args):
        pass  # pragma: no cover

    def on_answer(self, success, answer):
        pass  # pragma: no cover


class ClientCommand(Command):
    """ Client Command is a triple computation on a client:
          on_answer(execute(on_init()))
    """
    side = "client"

class MetaCommand(ServerCommand):
    """ MetaCOmmand is a ServerCommand that can manipulate the context of the command itself
    """
    side = "meta"

