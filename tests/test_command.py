import os, sys
from AVCommon.commands.server import BEGIN

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import command

from AVCommon.logger import logging


def test_commandSerialize():
    c = command.factory( ("BEGIN", False, "nothing") )
    s = c.serialize()
    cmd = command.unserialize(s)
    assert(not cmd.success)

    logging.debug("cmd: %s %s", cmd, type(cmd))
    assert(str(cmd).startswith("BEGIN"))

    #assert str(type(cmd)) == "<class 'AVCommon.Command_START.Command_START'>", "type: %s" % str(type(cmd))
    #assert str(type(cmd)) == "<class 'Command_START.Command_START'>", "type: %s" % str(type(cmd))

    command.factory( ("BEGIN", None, None) )
    try:
        command.factory( ("BEGIN", "", None) )
        assert(False)
    except:
        pass

def test_commandUnserialize():
    command.context = "mycontext"
    s = command.factory( "BEGIN" )
    logging.debug("Command: %s" % s)
    assert isinstance(s, command.Command), "type: %s not %s" % (type(s), command.Command)

    assert s.name == "BEGIN"
    assert s.args is None
    assert s.success is None
    assert s.side == "server", "side: %s" % s.side
    assert command.context == "mycontext", "wrong context: %s" % s.context
    assert s.timestamp

    s = command.factory( ["START_VM", None, ["kis", "mcafee"]] )
    assert s.name == "START_VM"
    assert s.args == ["kis", "mcafee"]
    assert s.success is None
    assert s.side == "server"
    assert command.context == "mycontext"

    s = command.factory( {"START_VM": ["kis", "mcafee"]} )
    assert s.name == "START_VM"
    assert s.args == ["kis", "mcafee"]
    assert s.success is None
    assert s.side == "server"
    assert command.context == "mycontext"

    s = command.factory( ["START_VM", None, ["kis", "mcafee"]] )
    assert s.name == "START_VM"
    assert s.args == ["kis", "mcafee"]
    assert s.success is None
    assert s.side == "server"
    assert command.context == "mycontext"

    s = command.factory( ("START_VM", True, ["kis", "mcafee"]) )
    assert s.name == "START_VM"
    assert not s.args
    assert s.result == ["kis", "mcafee"]
    assert s.success is True
    assert s.side == "server"
    assert command.context == "mycontext"

    s = command.factory( """('START_VM', True, ["kis", "mcafee"])""" )
    assert s.name == "START_VM"
    assert not s.args
    assert s.result == ["kis", "mcafee"]
    assert s.success is True
    assert s.side == "server"
    assert command.context == "mycontext"

    s.success = True
    q = command.factory( s )
    assert q.name == "START_VM"
    assert not q.args
    assert q.result == ["kis", "mcafee"]
    assert q.success is True
    assert q.side == "server"
    assert command.context == "mycontext"

    try:
        s = command.factory( )
        assert False, "should not unserialize this"
    except:
        pass
    try:
        s = command.factory( "A", 1, 2 )
        assert False, "should not unserialize this"
    except:
        pass
    try:
        s = command.factory( "B", True, 2 , 3 )
        assert False, "should not unserialize this"
    except:
        pass
    try:
        s = command.factory({"START_VM": ["kis", "mcafee"], "WHATEVER": []})
        assert False, "should not unserialize this"
    except:
        pass


def test_commandSerialization():
    c = command.factory( ["BEGIN", True, ['whatever','end']])
    s = c.serialize()

    cmd=command.unserialize(s)
    logging.debug("unserisalized: %s" % type(cmd.result))

    assert(cmd.success)
    assert(type(cmd.result) == list)
    assert(cmd.args == None)
    assert(cmd.result == ['whatever','end'])
    assert(str(cmd).startswith("BEGIN"))


def test_commandStart():
    c = command.factory("BEGIN")
    assert(c)
    assert(c.name == "BEGIN")

    #c.on_init("whatever")
    ret, answer = c.execute("vm", "arguments")
    #c.on_answer("vm", ret, answer)

if __name__ == '__main__':

    test_commandSerialize()
    test_commandStart()
    test_commandSerialization()
    test_commandUnserialize()

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))