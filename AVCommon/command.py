import sys, os
import inspect

import abc
import commands

#knownCommands = []
def initCommands():
        #print "DBG initCommands"
        #global knownCommands
        print dir(commands)
       
        cwd=os.getcwd()
        if cwd not in sys.path:
            sys.path.append(cwd)

        if(len(dir(commands)) > 6):
            return

        for py in [f[:-3] for f in os.listdir(cwd + "/commands") if f.startswith('Command_') and f.endswith('.py') and f != '__init__.py']:
            print "py: %s" % str(py)
            #print "commands: %s" % commands
            #print commands.__name__
            Command.knownCommands.append(py.split('_')[1])
            rpath = "%s.%s" % (commands.__name__, py)
            mod = __import__(rpath)
            #print "mod: %s" % mod
            classes = [getattr(mod, x) for x in dir(mod) if isinstance(getattr(mod, x), type)]
            for cls in classes:
                setattr(commands, cls.__name__, cls)
        print "DBG knownCommands: %s" % Command.knownCommands
        assert(len(dir(commands)) > 6)
        assert(len(Command.knownCommands) > 0)
        return

class Command():
    __metaclass__ = abc.ABCMeta

    knownCommands = []

    answer = ""
    OK="OK"
    KO="KO"

    """command"""
    def __init__(self, name):
        self.name = name
        initCommands()
        assert(len(dir(commands)) > 6)
        assert(len(Command.knownCommands) > 0)
    
    @staticmethod
    def unserialize(serialized):
        initCommands()
        assert(len(dir(commands)) > 6)

        ident, command, answer = serialized.split(',')
        assert(ident == "CMD")

        className = "Command_%s" % command
        print Command.knownCommands
        assert(command in Command.knownCommands)

        if command in Command.knownCommands:
            m = getattr(commands, className)
            c = getattr(m, className)
            cmd = c(command)
            cmd.answer = answer
            return cmd

    def serialize(self):
        return "CMD,%s,%s" % (self.name, self.answer)

    """ server side """
    @abc.abstractmethod
    def onInit(self):
        pass

    @abc.abstractmethod
    def onAnswer(self, answer):
        pass

    """ client side """
    @abc.abstractmethod
    def Execute(self):
        return self.answer

    def __str__(self):
        return self.name

