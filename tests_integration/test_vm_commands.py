__author__ = 'fabrizio'

import sys
import os
import logging
import logging.config
from time import sleep

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVCommon.procedure import Procedure
from AVCommon.command import Command

import logging
import logging.config

from AVCommon.procedure import Procedure
from AVCommon.mq import MQStar
from AVMaster.dispatcher import Dispatcher
from AVMaster.vm_manager import VMManager


def test_vm_commands():
    yaml = """

PSTART:
    - BEGIN
    - START_VM

PSTOP:
    - STOP_VM
    - END

TEST1:
    - START_VM
    - STOP_VM

TEST2:
    - BEGIN
    - START_VM
    - PUSH:
        - file_test1.sh
        - file_test2.dat
    - EXECUTE_VM: file_test1.sh hello world
    - PULL:
        - file_test1.out
    - STOP_VM
    - END

TEST3:
    - CALL: PSTART
    - SCREENSHOT
    - CALL: PSTOP
"""
    procedures = Procedure.load_from_yaml(yaml)

    test1 = Procedure.procedures["TEST3"]

    #vms = ["noav", "zenovm"]
    vms = ["noav"]
    redis_host = "localhost"
    mq = MQStar(redis_host)
    mq.clean()

    VMManager.vm_conf_file = "../AVMaster/conf/vms.cfg"
    dispatcher = Dispatcher(mq, vms)
    dispatcher.dispatch(test1)

if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    test_vm_commands()