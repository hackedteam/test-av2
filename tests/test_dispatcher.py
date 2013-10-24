import sys

sys.path.append("../AVCommon")
sys.path.append("../AVMaster")

from AVCommon.procedure import Procedure


def test_dispatcher():
    host = "localhost"

    vms = ["kis", "mcafee"]
    agentFiles = ["file.exe"]
    params = "parameters.json"

    update = Procedure("UPDATE", ["REVERT", "STARTVM", "UPDATE", "STOPVM"])

    dispatch = Procedure("DISPATCH", ["REVERT", "STARTVM", ("PUSH", agentFiles)])
    scout = Procedure("SCOUT", [
        ("PROCEDURE", "dispatch"),
        ("PUSH", agentFiles),
        ("START_AGENT", None),
        ("SET_PARAMS", params),
        ("BUILD", ["silent"]),
        ("EXECUTE_VM", ["build/agent.exe"]),
    ])


if __name__ == '__main__':
    test_dispatcher()
