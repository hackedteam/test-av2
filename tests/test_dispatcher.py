import sys, os
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import logging, logging.config

from AVCommon.procedure import Procedure
from AVCommon.mq import MQStar
from AVMaster.dispatcher import Dispatcher
from AVMaster.vm_manager import VMManager

def test_dispatcher():
    host = "localhost"

    vms = ["noav", "zenovm"]
    agentFiles = ["file.exe"]
    params = "parameters.json"

    update = Procedure("UPDATE", ["BEGIN", "REVERT", "START_VM", "UPDATE", "STOP_VM", "END"])

    dispatch = Procedure("DISPATCH", ["REVERT", "START_VM", ("PUSH", agentFiles)])
    scout = Procedure("SCOUT", [
        ("CALL", "dispatch"),
        ("PUSH", agentFiles),
        ("START_AGENT", None),
        ("COMMAND_CLIENT", ["BUILD_WINDOWS_SCOUT"]),
    ])

    host = "localhost"
    mq = MQStar(host)
    mq.clean()

    VMManager.vm_conf_file = "../AVMaster/conf/vms.cfg"
    dispatcher = Dispatcher(mq, vms)
    dispatcher.dispatch(update)


if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    test_dispatcher()
