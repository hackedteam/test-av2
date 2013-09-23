import sys
sys.path.append("../AVCommon")
sys.path.append("../AVMaster")

import Protocol
import MQ

from Procedure import Procedure
from Command import Command

import logging
import logging.config


procedures = {}

Procedure("UPDATE", ["REVERT", "STARTVM", "UPDATE", "STOPVM"]).add(procedures)
Procedure("DISPATCH", ["REVERT", "STARTVM", ("PUSH", agentFiles)]).add(procedures)
Procedure("SCOUT", [
                    ("PROCEDURE", "dispatch"),
                    ("PUSH", agentFiles),
                    ("START_AGENT", None),
                    ("SET_PARAMS", params),
                    ("BUILD", ["silent"]),
                    ("EXECUTE_AGENT", ["build/agent.exe"]),
        ]).add(procedures)



