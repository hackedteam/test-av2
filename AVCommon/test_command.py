from Command import Command

import os
import commands

def test_commandAbstract():
    try:
        c = Command("START")
        assert("Should not be able to instance an abstract class" is False)
    except Exception:
        pass

def test_commandSerialize():
    c = Command.unserialize( ("START","OK","nothing") )
    s = c.serialize()
    cmd = Command.unserialize(s)

    print "cmd: ", cmd, type(cmd)
    assert(str(cmd) == "START")

    print "type: ", type(cmd)
    assert(str(type(cmd)) == "<class 'Command_START.Command_START'>")

def test_commandAnswer():
    c = Command.unserialize( ["START","OK",['whatever','end']])
    s = c.serialize()
    assert(len(s) == 3)
    cmd = Command.unserialize(s)
    print "unserisalized: %s" % type(cmd.answer)
    assert(type(cmd.answer) == list)
    assert(cmd.answer == ['whatever','end'])
    assert(str(cmd) == "START")


def test_commandStart():
    import Command_START
    c = Command_START.Command_START("START")
    assert(c)
    assert(c.name == "START")

    c.onInit()
    c.onAnswer(c.Execute())

if __name__ == '__main__':
    test_commandSerialize()
    test_commandStart()
    test_commandAnswer()
    test_commandAbstract()
