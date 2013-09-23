import sys
sys.path.append("../AVCommon")

import Protocol
import MQ
from Command import Command

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import logging

import pprint
pp = pprint.PrettyPrinter(indent=4)


class Procedure :
    proc = []
    name = ""

    """docstring for Procedure"""
    def __init__(self, name, proc=[]):
        self.name = name
        self.proc = [Command.unserialize(c) for c in proc]

    def nextCommand(self):
        return self.proc.pop(0)

    def empty(self):
        return self.proc == []

    def __length__(self):
        return len(self.proc)

    @staticmethod
    def loadFromYaml(stream):
        procedures = {}
        data = load(stream, Loader=Loader)
        pp.pprint(data)
        for name in data.keys():
            commandList = []
            commandData = data[name]
            logging.debug("new procedure: %s\nargs: %s" % (name, data[name]))
            for c in commandData:
                c = Command.unserialize(c)
                commandList.append(c)
                logging.debug("  command: %s" % c)

            procedures[name] = Procedure(commandList)
        return procedures

    @staticmethod
    def loadFromFile(filename):
        stream = file(filename, 'r')
        return loadFromYaml(strema)
