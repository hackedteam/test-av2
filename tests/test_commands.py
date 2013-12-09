from AVCommon.commands.client import SET

__author__ = 'fabrizio'

import sys
import os

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVCommon.logger import logging

from AVCommon import command

command.init()

def test_commands():
    #command.context = {}

    s = command.factory("SET")
    s.vm = "vm"

    s.execute("vm", {"ciao":"mondo"})
    logging.debug(command.context)

    assert "ciao" in command.context
    assert command.context["ciao"] == "mondo"

    s = command.factory("SET")
    s.vm = "vm"
    s.execute( s.vm, {"pippo":"franco", "hello":"world", "number":"123"})
    assert "ciao" in command.context
    assert command.context["ciao"] == "mondo"

    logging.debug(command.context)

if __name__ == '__main__':

    test_commands()