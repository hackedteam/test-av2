import os, sys
prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import Protocol
from AVCommon import MQ

from Procedure import Procedure
from AVCommon.Command import Command

def test_dispatcher():
    c = Command.unserialize( ["START", True, ['whatever','end']])

    update = Procedure("UPDATE", ["REVERT", "STARTVM", "UPDATE", "STOPVM"])
    dispatch = Procedure("DISPATCH", ["REVERT", "STARTVM", ("PUSH", agentFiles)])
    scout = Procedure("SCOUT", [
                        ("PROCEDURE", "dispatch"),
                        ("PUSH", agentFiles),
                        ("STARTAGENT", None),
                        ("SET_PARAMS", params),
                        ("BUILD", ["silent"]),
                        ("EXECUTE", ["build/agent.exe"]),
                    ])

    assert update
    assert dispatch
    assert scout

if __name__ == '__main__':
    test_dispatcher()
