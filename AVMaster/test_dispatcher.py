from vmManager import *

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import Protocol
from AVCommon import MQ


def test_dispatcher():
    v = vmManager()
    host = "localhost"

    vms = ["kis", "mcafee"]

    update = Procedure("UPDATE", [ "REVERT", "STARTVM", "UPDATE", "STOPVM" ] )


    dispatch = Procedure("DISPATCH", [ "REVERT", "STARTVM", ("PUSH", agentFiles) ] )
    scout = Procedure("SCOUT", [
                        ("PROCEDURE", "dispatch"),
                        ("PUSH", agentFiles),
                        ("STARTAGENT", None),
                        ("SET_PARAMS", params),
                        ("BUILD", ["silent"]),
                        ("EXECUTE", ["build/agent.exe"]),
                    ])
    d = dispatcher()

if __name__ == '__main__':
    test_dispatcher()
