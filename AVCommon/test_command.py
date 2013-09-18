from Command import Command

import os
import commands

def test_commandSerialize():
    try:
        c = Command("START")
        assert("Should not be able to instance an abstract class" is False)
    except Exception:
        pass

    c = Command.unserialize("CMD,START,")
    s = c.serialize()
    cmd = Command.unserialize(s)

    print cmd, type(cmd)
    assert(str(cmd) == "START")

    print type(cmd)
    assert(str(type(cmd)) == "<class 'Command_START.Command_START'>")


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
