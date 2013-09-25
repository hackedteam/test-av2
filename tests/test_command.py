import sys
sys.path.append("../AVCommon")

from Command import Command

import os
import commands
import logging, sys
import logging.config

def test_commandAbstract():
    try:
        c = Command("START")
        assert("Should not be able to instance an abstract class" is False)
    except Exception:
        pass

def test_commandSerialize():
    c = Command.unserialize( ("START", False, "nothing") )
    s = c.serialize()
    cmd = Command.unserialize(s)
    assert(not cmd.success)

    logging.debug("cmd: %s %s", cmd, type(cmd))
    assert(str(cmd).startswith("START"))

    logging.debug("type: %s", type(cmd))
    assert(str(type(cmd)) == "<class 'Command_START.Command_START'>")

    Command.unserialize( ("START", None, None) )
    try:
        Command.unserialize( ("START", "", None) )
        assert(False)
    except:
        pass

def test_commandUnserialize():
    Command.context = "mycontext"
    s = Command.unserialize( "START" )
    assert s.name == "START"
    assert s.payload is None
    assert s.success is None
    assert s.side == "client"
    assert s.context == "mycontext"

    s = Command.unserialize( ["STARTVM", None, ["kis", "mcafee"]] )
    assert s.name == "STARTVM"
    assert s.payload == ["kis", "mcafee"]
    assert s.success is None
    assert s.side == "server"
    assert s.context == "mycontext"

    s = Command.unserialize( {"STARTVM": ["kis", "mcafee"]} )
    assert s.name == "STARTVM"
    assert s.payload == ["kis", "mcafee"]
    assert s.success is None
    assert s.side == "server"
    assert s.context == "mycontext"

    s = Command.unserialize( ["STARTVM", ["kis", "mcafee"]] )
    assert s.name == "STARTVM"
    assert s.payload == ["kis", "mcafee"]
    assert s.success is None
    assert s.side == "server"
    assert s.context == "mycontext"

    s = Command.unserialize( ("STARTVM", True, ["kis", "mcafee"]) )
    assert s.name == "STARTVM"
    assert s.payload == ["kis", "mcafee"]
    assert s.success is True
    assert s.side == "server"
    assert s.context == "mycontext"

    s = Command.unserialize( """('STARTVM', True, ["kis", "mcafee"])""" )
    assert s.name == "STARTVM"
    assert s.payload == ["kis", "mcafee"]
    assert s.success is True
    assert s.side == "server"
    assert s.context == "mycontext"

    s.success = True
    q = Command.unserialize( s )
    assert q.name == "STARTVM"
    assert q.payload == ["kis", "mcafee"]
    assert q.success is True
    assert q.side == "server"
    assert q.context == "mycontext"

    try:
        s = Command.unserialize( )
        assert False, "should not unserialize this"
    except:
        pass
    try:
        s = Command.unserialize( "A", 1, 2 )
        assert False, "should not unserialize this"
    except:
        pass
    try:
        s = Command.unserialize( "B", True, 2 , 3 )
        assert False, "should not unserialize this"
    except:
        pass
    try:
        s = Command.unserialize({"STARTVM": ["kis", "mcafee"], "WHATEVER": []})
        assert False, "should not unserialize this"
    except:
        pass



def test_commandAnswer():
    c = Command.unserialize( ["START", True, ['whatever','end']])
    s = c.serialize()
    assert(len(s) == 3)
    cmd = Command.unserialize(s)
    logging.debug("unserisalized: %s" % type(cmd.payload))

    assert(cmd.success)
    assert(type(cmd.payload) == list)
    assert(cmd.payload == ['whatever','end'])
    assert(str(cmd).startswith("START"))


def test_commandStart():
    import Command_START
    c = Command_START.Command_START("START")
    assert(c)
    assert(c.name == "START")

    c.on_init("whatever")
    ret, answer = c.execute("arguments")
    c.on_answer(ret, answer)

if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    test_commandSerialize()
    test_commandStart()
    test_commandAnswer()
    test_commandAbstract()
    test_commandUnserialize()
