import sys, os

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVCommon.procedure import Procedure


def test_dispatcher():
    host = "localhost"

    vms = ["kis", "mcafee"]
    agentFiles = ["file.exe"]
    params = "parameters.json"

    update = Procedure("UPDATE", ["REVERT", "START_VM", "UPDATE", "STOP_VM"])

    dispatch = Procedure("DISPATCH", ["REVERT", "START_VM", ("PUSH", agentFiles)])
    scout = Procedure("SCOUT", [
        ("CALL", "dispatch"),
        ("PUSH", agentFiles),
        ("START_AGENT", None),
        ("COMMAND_CLIENT", ["BUILD_WINDOWS_SCOUT"]),
    ])


if __name__ == '__main__':
    test_dispatcher()
