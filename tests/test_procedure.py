import sys

sys.path.append("../AVCommon")
sys.path.append("../AVMaster")

from AVCommon.procedure import Procedure
from AVCommon.command import Command

import logging
import logging.config


def test_dispatcher():
    c = Command.unserialize(["START", True, ['whatever', 'end']])
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


def test_procedure_file():
    procedures = Procedure.load_from_file("../AVCommon/procedures.yaml")
    assert procedures, "empty procedures"
    logging.debug("procedures: %s" % procedures)
    for p in procedures.values():
        assert isinstance(p, Procedure), "not a Procedure: %s" % p


def test_procedure_yaml():
    yaml = """UPDATE:
    - REVERT
    - STARTVM
    - UPDATE
    - STOPVM

DISPATCH:
    - REVERT
    - STARTVM
    - UPDATE
    - PUSH:
        - file.sh
        - anotherfile.sh

SCOUT:
    - PROCEDURE: DISPATCH
    - START_AGENT
    - SET_PARAMS:
        - kind: scout
        - platform: windows
"""
    procedures = Procedure.load_from_yaml(yaml)
    assert procedures, "empty procedures"
    logging.debug("procedures: %s" % procedures)
    for p in procedures.values():
        assert isinstance(p, Procedure), "not a Procedure: %s" % p


if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    test_procedure_file()
    test_procedure_yaml()
    test_dispatcher()
