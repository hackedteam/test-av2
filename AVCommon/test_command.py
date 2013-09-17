from Command import Command
#from commands import Command_START
import os
import commands

def test_command():
    c = Command("START")
    s = c.serialize()
    cmd = Command.unserialize(s)

    print cmd, type(cmd)
    assert(str(cmd) == "START")
    assert(type(cmd) == type(c))

def test_commandStart():
    print commands
    c=Command_START.Command_START()

def listModules():
    #import os
    #print commands.__path__[0]
    #for f in os.listdir(commands.__path__[0]):
    #    print f
    for py in [f[:-3] for f in os.listdir(commands.__path__[0]) if f.endswith('.py') and f != '__init__.py']:
        print "py: %s" % str(py)
        mod = __import__("commands.%s" % py)
        classes = [getattr(mod, x) for x in dir(mod) if isinstance(getattr(mod, x), type)]
        for cls in classes:
            setattr(commands, cls.__name__, cls)
    print dir(commands)

if __name__ == '__main__':
    #listModules()
    #test_commandStart()
    #print dir(commands)
    test_command()
