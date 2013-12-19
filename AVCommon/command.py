import sys
import os
from AVCommon.logger import logging
import ast
import re
import abc
from types import ModuleType
from AVCommon import config
import commands
import inspect
import glob
import time
import pickle
import importlib

import base64

inspect_getfile = inspect.getfile(inspect.currentframe())
cmd_folder = os.path.split(os.path.realpath(os.path.abspath(inspect_getfile)))[0]
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
parent = os.path.split(cmd_folder)[0]
if parent not in sys.path:
    sys.path.insert(0, parent)

known_commands = {}
context = {}


def init():
    global command_names
    global known_commands
    #logging.debug("initCommands")

    commands = []
    for d in ["AVAgent", "AVCommon", "AVMaster"]:
        for side in ["server", "client", "meta"]:
            search = os.path.join(parent, d, "commands", side, "*.py")
            dcommands = glob.glob(search)
            for dc in dcommands:
                name_file = os.path.split(dc)[1]
                name = os.path.splitext(name_file)[0]
                if name.startswith("__init__"):
                    continue

                path = "%s.%s.%s.%s" % (d, "commands", side, name)
                commands.append((name, side, path))
                #logging.debug("%s" % (name))

    for name, side, path in commands:
        m = importlib.import_module(path)
        m.side = side
        known_commands[name] = m

    logging.info("Commands: %s" % known_commands.keys())


def normalize(data):
    """ a command cane be unserialized in many ways:
    - command instance
    - dict: { command: payload }
    - tuple/array: (cmd, success, payload) or (cmd, payload)
    - str: "(cmd, success, payload)"

    payload is evaluated via ast, so that it can contain a type like tuple, array, number, dict and so on
    if payload begins with a "|", it's considered a plain string and it's not evaluated
    """
    #ident, command, answer = serialized.split(',', 2)
    #assert(ident == "CMD")
    cmd = data
    success = None
    args = None
    result = None
    vm = None

    assert data, "cannot normalize a null argument"

    identified = "instance"
    if isinstance(data, Command):
        logging.warn("normalizing a command")
        return data.name, data.success, data.args, data.result, data.vm
    elif isinstance(data, dict):
        identified = "dict"
        assert len(data) == 1
        cmd = data.keys()[0]
        args = data[cmd]
    elif not isinstance(data, str) and len(data) == 3:
        identified = "len 3"
        cmd, success, payload = data
        if success == None:
            args = payload
        else:
            result = payload

    elif isinstance(data, str):
        identified = "str"
        m = re.compile("\('(\w+)\', (\w+), (.+)\)").match(data)
        if m:
            identified = "reg"
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
            if success == None:
                args = payload
            else:
                result = payload

    #logging.debug(1)Command.knownCommands

    if config.verbose:
        logging.debug("identified: %s" % identified)
    assert isinstance(success, bool) or success is None, "success: %s" % success
    assert isinstance(cmd, str), "not a string: %s" % cmd

    return (cmd, success, args, result, vm)


def factory(data):
    if not known_commands:
        init()

    name, success, args, result, vm = normalize(data)

    return _factory(name, success, args, result, vm)


def eval_safe(attr,  value):

    if isinstance(value, str) and attr.startswith("|"):
        a = value[1:]
    else:
        try:
            a = ast.literal_eval(value)
        except:
            a = value

    attr = a


def _factory(name, success, args, result,  vm, timestamp = None):
    assert name in known_commands.keys(), "Unknown command: %s" % name

    m = known_commands[name]
    if not timestamp:
        logging.debug("new timestamp required")
        timestamp=time.time()
    c = Command(name, success, args, result, vm, m.side, timestamp)

    c.execute = m.execute
    if c.side == "client":
        c.on_answer = m.on_answer
        c.on_init = m.on_init
    else:
        c.on_answer = lambda x, y, z: None
        c.on_init = lambda x, y, z: None

    # payload eval in safe way
    eval_safe(c.args, args)
    eval_safe(c.result, result)

    return c


def unserialize(message):
    data = base64.b64decode(message)

    name, success, args, result, vm, side, timestamp = pickle.loads(data)
    if config.verbose:
        logging.debug("unserialized: (%s,%s,%s,%s,%s,%s)" % (name, success, args, str(result)[:50], vm, timestamp))
    return _factory(name, success, args, result, vm, timestamp)


class Command(object):
    """ A Command is a base class for any instruction to give on a channel.
    A command is defined by a name and an implementation class. Each class can be Server, Client or Meta.

    """
    success = None

    side = None
    vm = None

    def __init__(self, name, success=None, args="", result=None, vm=None, side=None,  timestamp=None):
        """ A command is constructed with a name, that identifies the derived class """
        self.name = name
        self.success = success
        self.args = args
        self.result = result
        if not timestamp:
            self.timestamp = time.time()
        else:
            self.timestamp = timestamp
        self.vm = vm
        self.side = side

    def serialize(self):
        serialized = pickle.dumps(( self.name, self.success, self.args, self.result, self.vm, self.side, self.timestamp ),
                                  pickle.HIGHEST_PROTOCOL)
        #logging.debug("pickle.dumps(%s)" % serialized)
        return base64.b64encode(serialized)

    def __str__(self):
        ts = time.strftime("%y%m%d-%H%M%S", time.localtime(self.timestamp))
        return "%s, %s, %s, %s, %s" % (self.name, self.success, ts, self.args, self.result)
