import sys, os
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVCommon.procedure import Procedure
from AVCommon.command import Command

from AVCommon import command

from AVCommon.logger import logging

def test_dispatcher():
    c = command.factory(["BEGIN", True, ['whatever', 'end']])
    agentFiles = ""
    params = ""

    update = Procedure("UPDATE", ["REVERT", "START_VM", "RELOG", "STOP_VM"])
    dispatch = Procedure("DISPATCH", ["REVERT", "START_VM", ("PUSH", None, agentFiles)])
    scout = Procedure("SCOUT", [
        ("CALL", None, "dispatch"),
        ("PUSH", None, agentFiles),
    ])

    assert update
    assert dispatch
    assert scout

def test_procedure_insert():
    c = command.factory(["BEGIN", True, ['whatever', 'end']])
    agentFiles = ""
    params = ""

    p1 = Procedure("UPDATE", ["REVERT", "START_VM", "RELOG", "STOP_VM"])
    p2 = Procedure("DISPATCH", ["REVERT", "START_VM", ("PUSH", None, agentFiles)])

    lp1= len(p1)
    lp2= len(p2)

    p1.insert(p2)

    assert p1
    assert p2
    assert len(p1) == lp1 + lp2

def test_procedure_file():
    procedures = Procedure.load_from_file("../AVMaster/conf/procedures/procedures.yaml")
    assert procedures, "empty procedures"
    logging.debug("procedures: %s" % procedures)
    for p in procedures.values():
        assert isinstance(p, Procedure), "not a Procedure: %s" % p


def test_procedure_yaml():
    yaml = """UPDATE:
    - REVERT
    - START_VM
    - RELOG
    - STOP_VM

DISPATCH:
    - REVERT
    - START_VM
    - RELOG
    - PUSH:
        - file.sh
        - anotherfile.sh

SCOUT:
    - CALL: DISPATCH
    - START_AGENT
    - BUILD
"""
    procedures = Procedure.load_from_yaml(yaml)
    assert procedures, "empty procedures"
    logging.debug("procedures: %s" % procedures)
    assert len(procedures) == 3, "wrong procedures number: %s" % len(procedures)

    for p in procedures.values():
        assert isinstance(p, Procedure), "not a Procedure: %s" % p
        assert p.name
        assert p.command_list
        assert len(p) == len(p.command_list)

    leninstance = len(procedures.values())
    lenstatic = len(Procedure.procedures)
    assert leninstance == lenstatic, "different lengths: %s!=%s" %(leninstance, lenstatic)


if __name__ == '__main__':

    test_procedure_file()
    test_procedure_yaml()
    test_dispatcher()
