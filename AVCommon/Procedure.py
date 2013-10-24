import sys

sys.path.append("../AVCommon")

from command import Command

from yaml import load

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import logging

import pprint

pp = pprint.PrettyPrinter(indent=4)


class Procedure:
    proc = []
    name = ""

    """docstring for Procedure"""

    def __init__(self, name, proc=None):
        self.name = name
        if not proc:
            self.proc = []
        else:
            self.proc = [Command.unserialize(c) for c in proc]

    def next(self):
        for c in self.proc:
            yield c

    def next_command(self):
        c = self.proc.pop(0)
        return c

    def __len__(self):
        return len(self.proc)

    @staticmethod
    def load_from_yaml(stream):
        procedures = {}
        data = load(stream, Loader=Loader)
        pp.pprint(data)
        for name in data.keys():
            command_list = []
            command_data = data[name]
            logging.debug("new procedure: %s\nargs: %s" % (name, data[name]))
            for c in command_data:
                c = Command.unserialize(c)
                command_list.append(c)
                logging.debug("  command: %s" % c)

            procedures[name] = Procedure(command_list)
        return procedures

    @staticmethod
    def load_from_file(filename):
        stream = file(filename, 'r')
        return Procedure.load_from_yaml(stream)
