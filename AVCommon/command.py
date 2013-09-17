import sys, os
import inspect
import commands

class Command():
    answer = ""
    OK="OK"
    KO="KO"

    knownCommands = []

    """command"""
    def __init__(self, name):
        self.name = name
        print dir(commands)
        if(len(dir(commands)) == 6):
            self._initCommands()

    def _initCommands(self):
        print "DBG _initCommands"
        for py in [f[:-3] for f in os.listdir(commands.__path__[0]) if f.endswith('.py') and f != '__init__.py']:
            print "py: %s" % str(py)
            self.knownCommands.append(py)
            mod = __import__("commands.%s" % py)
            classes = [getattr(mod, x) for x in dir(mod) if isinstance(getattr(mod, x), type)]
            for cls in classes:
                setattr(commands, cls.__name__, cls)

    def unserialize(serialized):
        ident, command, answer = serialized.split(',')
        assert(ident == "CMD")

        className = "Command_%s" % command
        if className in self.knownCommands:
            m = commands.getattr(className)
            c = m.getattr(className)
            cmd = c(command)
            cmd.answer = answer

            return cmd

        #g = globals().copy()
        #for name, obj in g.iteritems():
        #    print name,obj

        for module in sys.modules.keys():
            break
            #if module.startswith("Command_"):
            print module
            #current_module = sys.modules[__name__]
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj):
                    print "   %s" % obj

        c.answer = answer
        return c

    def serialize(self):
        return "CMD,%s,%s" % (self.name, self.answer)

    """ server side """
    def onInit(self):
        pass

    """ client side """
    def onReceive(self):
        return self.answer

    def __str__(self):
        return self.name

    unserialize = staticmethod(unserialize)




