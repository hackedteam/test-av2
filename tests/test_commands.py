__author__ = 'fabrizio'

import sys
import os

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import logging
import logging.config

from AVAgent.Command_SET import Command_SET
from AVAgent.Command_GET import Command_GET

from AVCommon import command


def test_commands():
    #command.context = {}

    s = Command_SET("SET")
    s.vm = "vm"

    s.execute([("ciao","mondo")])
    logging.debug(command.context)

    assert "ciao" in command.context
    assert command.context["ciao"] == "mondo"

    s = Command_SET("SET")
    s.vm = "vm"
    s.execute([["pippo","franco"], ["hello","world"], ("number","123")])
    assert "ciao" in command.context
    assert command.context["ciao"] == "mondo"

    logging.debug(command.context)

if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    test_commands()