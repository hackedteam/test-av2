from AVCommon.commands.client import SET

__author__ = 'fabrizio'

import sys
import os

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVCommon.logger import logging

from AVCommon import command
from AVCommon import helper

command.init()

def test_START_VM():
    procs = """Process list: 40
pid=0, owner=, cmd=[System Process]
pid=4, owner=NT AUTHORITY\SYSTEM, cmd=System
pid=264, owner=NT AUTHORITY\SYSTEM, cmd=smss.exe
pid=360, owner=NT AUTHORITY\SYSTEM, cmd=csrss.exe
pid=400, owner=NT AUTHORITY\SYSTEM, cmd=wininit.exe
pid=412, owner=NT AUTHORITY\SYSTEM, cmd=csrss.exe
pid=480, owner=NT AUTHORITY\SYSTEM, cmd=services.exe
pid=488, owner=NT AUTHORITY\SYSTEM, cmd=lsass.exe
pid=500, owner=NT AUTHORITY\SYSTEM, cmd=lsm.exe
pid=508, owner=NT AUTHORITY\SYSTEM, cmd=winlogon.exe
pid=624, owner=NT AUTHORITY\SYSTEM, cmd=svchost.exe
pid=696, owner=NT AUTHORITY\NETWORK SERVICE, cmd=svchost.exe
pid=748, owner=NT AUTHORITY\LOCAL SERVICE, cmd=svchost.exe
pid=844, owner=NT AUTHORITY\SYSTEM, cmd=svchost.exe
pid=872, owner=NT AUTHORITY\LOCAL SERVICE, cmd=svchost.exe
pid=896, owner=NT AUTHORITY\SYSTEM, cmd=svchost.exe
pid=396, owner=NT AUTHORITY\NETWORK SERVICE, cmd=svchost.exe
pid=316, owner=NT AUTHORITY\SYSTEM, cmd=spoolsv.exe
pid=1048, owner=NT AUTHORITY\SYSTEM, cmd=sched.exe
pid=1084, owner=NT AUTHORITY\LOCAL SERVICE, cmd=svchost.exe
pid=1232, owner=NT AUTHORITY\SYSTEM, cmd=avguard.exe
pid=1308, owner=NT AUTHORITY\SYSTEM, cmd=cmd.exe
pid=1316, owner=NT AUTHORITY\SYSTEM, cmd=rubyw.exe
pid=1472, owner=WIN7AVIRA\avtest, cmd=taskhost.exe
pid=1556, owner=WIN7AVIRA\avtest, cmd=Dwm.exe
pid=1564, owner=WIN7AVIRA\avtest, cmd=Explorer.EXE
pid=1732, owner=WIN7AVIRA\avtest, cmd=VMwareTray.exe
pid=1764, owner=WIN7AVIRA\avtest, cmd=vmtoolsd.exe
pid=1856, owner=WIN7AVIRA\avtest, cmd=cmd.exe
pid=1864, owner=WIN7AVIRA\avtest, cmd=conhost.exe
pid=1884, owner=WIN7AVIRA\avtest, cmd=python.exe
pid=1924, owner=NT AUTHORITY\SYSTEM, cmd=cmd.exe
pid=1940, owner=NT AUTHORITY\SYSTEM, cmd=conhost.exe
pid=1972, owner=NT AUTHORITY\SYSTEM, cmd=ruby.exe
pid=2012, owner=NT AUTHORITY\SYSTEM, cmd=vmtoolsd.exe
pid=1352, owner=, cmd=taskhost.exe
pid=1372, owner=WIN7AVIRA\avtest, cmd=Updater.exe
pid=948, owner=WIN7AVIRA\avtest, cmd=avgnt.exe
pid=1936, owner=NT AUTHORITY\NETWORK SERVICE, cmd=WmiPrvSE.exe
pid=2064, owner=, cmd=dllhost.exe"""
    processes = helper.convert_processes(procs)
    assert processes
    for p in processes:
        assert len(p) == 3
        assert "pid" in p.keys()
        assert "owner" in p.keys()
        assert "name" in p.keys()

def test_command_SET():
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


def test_command_SLEEP():
    #command.context = {}

    s = command.factory("SLEEP")
    s.vm = "vm"

    s.execute("vm", "protocol", {"ciao":"mondo"})
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
    test_START_VM()
    test_command_SET()