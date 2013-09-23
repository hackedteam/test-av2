import sys
sys.path.append("../AVCommon")
sys.path.append("../AVMaster")

import Protocol
import MQ

from Procedure import Procedure
from Command import Command

import logging
import logging.config

def test_dispatcher():
    c = Command.unserialize( ["START", True, ['whatever','end']])
    agentFiles = ""
    params = ""

    update = Procedure("UPDATE", ["REVERT", "STARTVM", "UPDATE", "STOPVM"])
    dispatch = Procedure("DISPATCH", ["REVERT", "STARTVM", ("PUSH", agentFiles)])
    scout = Procedure("SCOUT", [
                        ("PROCEDURE", "dispatch"),
                        ("PUSH", agentFiles),
                        ("START_AGENT", None),
                        ("SET_PARAMS", params),
                        ("BUILD", ["silent"]),
                        ("EXECUTE_AGENT", ["build/agent.exe"]),
                    ])

    assert update
    assert dispatch
    assert scout

if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    test_dispatcher()
