__author__ = 'zeno'
import sys, os
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())
from AVCommon.protocol import ProtocolClient, Protocol
from AVCommon.command import Command
from AVCommon.mq import MQStar
from AVCommon.procedure import Procedure

from mock import MagicMock
from AVCommon.logger import logging


def notest_mock():
    ProtocolClient._executeCommand = MagicMock(return_value=(True,None))
    command = Command.unserialize(("EVAL_SERVER",None,"dir()"));
    assert command

    success,ret = ProtocolClient._executeCommand(command)
    assert success
    assert not ret
    ProtocolClient._executeCommand.assert_called()

    #Protocol._execute = MagicMock(return_value=(True,None))


def notest_ProtocolEval():
    host = "localhost"
    mq = MQStar(host)
    mq.clean()
    c = "client1"
    mq.add_client(c)

    commands = ["BEGIN", ("EVAL_SERVER", "dir()"),
                ("EVAL_SERVER", "locals()"),
                ("EVAL_SERVER", "__import__('os').getcwd()"),
                ("END", None, None)]
    procedure = Procedure("PROC", commands)

    p = Protocol(mq, c, procedure)

    while p.send_next_command():
        logging.debug("sent command")

    exit = False
    while not exit:
        rec = mq.receive_server(blocking=True, timeout=10)
        if rec is not None:
            logging.debug("- SERVER RECEIVED %s %s" % (rec, type(rec)))
            c, msg = rec
            answer = p.receive_answer(c, msg)
            logging.debug("- SERVER RECEIVED ANSWER: ", answer.success)
            if answer.name == "END" or not answer.success:
                logging.debug("- SERVER RECEIVE END")
                #if answer.success:
            a = """('client1', ('EVAL_SERVER', True, {'self': <Command_EVAL_SERVER.Command_EVAL_SERVER object at 0x10931f810>, 'args': 'locals()'}))"""#   p.send_next_command()

        else:
            logging.debug("- SERVER RECEIVED empty")
            exit = True

if __name__ == "__main__":


    notest_mock()
    notest_ProtocolEval()


