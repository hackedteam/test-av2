import sys
sys.path.append("../AVCommon")

from AVCommon.command import Command

import logging
import logging.config

def test_commandAbstract():
    try:
        c = Command("BEGIN")
        assert("Should not be able to instance an abstract class" is False)
    except Exception:
        pass

def test_commandSerialize():
    c = Command.unserialize( ("BEGIN", False, "nothing") )
    s = c.serialize()
    cmd = Command.unserialize(s)
    assert(not cmd.success)

    logging.debug("cmd: %s %s", cmd, type(cmd))
    assert(str(cmd).startswith("BEGIN"))

    #assert str(type(cmd)) == "<class 'AVCommon.Command_START.Command_START'>", "type: %s" % str(type(cmd))
    #assert str(type(cmd)) == "<class 'Command_START.Command_START'>", "type: %s" % str(type(cmd))

    Command.unserialize( ("BEGIN", None, None) )
    try:
        Command.unserialize( ("BEGIN", "", None) )
        assert(False)
    except:
        pass

def test_commandUnserialize():
    Command.context = "mycontext"
    s = Command.unserialize( "BEGIN" )
    logging.debug("Command: %s" % s)
    assert isinstance(s, Command), "type: %s not %s" % (dir(s.__class__), Command)

    assert s.name == "BEGIN"
    assert s.payload is None
    assert s.success is None
    assert s.side == "server"
    assert s.context == "mycontext", "wrong context: %s" % s.context

    s = Command.unserialize( ["START_VM", None, ["kis", "mcafee"]] )
    assert s.name == "START_VM"
    assert s.payload == ["kis", "mcafee"]
    assert s.success is None
    assert s.side == "server"
    assert s.context == "mycontext"

    s = Command.unserialize( {"START_VM": ["kis", "mcafee"]} )
    assert s.name == "START_VM"
    assert s.payload == ["kis", "mcafee"]
    assert s.success is None
    assert s.side == "server"
    assert s.context == "mycontext"

    s = Command.unserialize( ["START_VM", ["kis", "mcafee"]] )
    assert s.name == "START_VM"
    assert s.payload == ["kis", "mcafee"]
    assert s.success is None
    assert s.side == "server"
    assert s.context == "mycontext"

    s = Command.unserialize( ("START_VM", True, ["kis", "mcafee"]) )
    assert s.name == "START_VM"
    assert s.payload == ["kis", "mcafee"]
    assert s.success is True
    assert s.side == "server"
    assert s.context == "mycontext"

    s = Command.unserialize( """('START_VM', True, ["kis", "mcafee"])""" )
    assert s.name == "START_VM"
    assert s.payload == ["kis", "mcafee"]
    assert s.success is True
    assert s.side == "server"
    assert s.context == "mycontext"

    s.success = True
    q = Command.unserialize( s )
    assert q.name == "START_VM"
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
        s = Command.unserialize({"START_VM": ["kis", "mcafee"], "WHATEVER": []})
        assert False, "should not unserialize this"
    except:
        pass


def test_commandAnswer():
    c = Command.unserialize( ["BEGIN", True, ['whatever','end']])
    s = c.serialize()
    assert(len(s) == 3)
    cmd = Command.unserialize(s)
    logging.debug("unserisalized: %s" % type(cmd.payload))

    assert(cmd.success)
    assert(type(cmd.payload) == list)
    assert(cmd.payload == ['whatever','end'])
    assert(str(cmd).startswith("BEGIN"))


def test_commandStart():
    from AVCommon import Command_BEGIN

    c = Command_BEGIN.Command_BEGIN("BEGIN")
    assert(c)
    assert(c.name == "BEGIN")

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
