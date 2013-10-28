import sys

sys.path.append("../AVCommon")
sys.path.append("../AVMaster")

from AVCommon.procedure import Procedure
from AVCommon.command import Command

import logging
import logging.config


def test_dispatcher():
    c = Command.unserialize(["BEGIN", True, ['whatever', 'end']])
    agentFiles = ""
    params = ""

    update = Procedure("UPDATE", ["REVERT", "START_VM", "UPDATE", "STOP_VM"])
    dispatch = Procedure("DISPATCH", ["REVERT", "START_VM", ("PUSH", agentFiles)])
    scout = Procedure("SCOUT", [
        ("CALL", "dispatch"),
        ("PUSH", agentFiles),
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
    - START_VM
    - UPDATE
    - STOP_VM

DISPATCH:
    - REVERT
    - START_VM
    - UPDATE
    - PUSH:
        - file.sh
        - anotherfile.sh

SCOUT:
    - CALL: DISPATCH
    - START_AGENT
    - COMMAND_CLIENT:
      - SCOUT_BUILD_WINDOWS_SILENT
      - EXECUTE_SCOUT
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
