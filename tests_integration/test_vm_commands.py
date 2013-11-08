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
from AVMaster import vm_manager
 
def test_vm_commands():
    yaml = """

TEST1:
    - START_VM
 
TEST2:
    - EXECUTE_VM: c:\\users\\avtest\\desktop\\pubsub\\started.bat
    - PUSH:
        - /tmp/gggg
        - c:\\users\\avtest\\desktop\\ddd.txt
    - SCREENSHOT: /tmp/maggic_path.png
    - PULL:
        - c:\\users\\avtest\\desktop\\ggggg.txt
        - /tmp/jojojo
 
TEST3:
    - STOP_VM
 
TEST4:
    - START_VM
    - SCREENSHOT: /tmp/magic_img_path.png
    - STOP_VM
"""
    procedures = Procedure.load_from_yaml(yaml)
 
    #vms = ["noav", "zenovm"]
    vms = ["noav"]
    redis_host = "localhost"
    mq = MQStar(redis_host)
    mq.clean()
 
    vm_manager.vm_conf_file = "../AVMaster/conf/vms.cfg"
    dispatcher = Dispatcher(mq, vms)
    logging.info("STARTING TEST 1")
    dispatcher.dispatch(procedures["TEST1"])

    import time
    time.sleep(200)

    logging.info("STARTING TEST 2")
    dispatcher.dispatch(procedures["TEST2"])

    time.sleep(30)

    logging.info("STARTING TEST 3")
    dispatcher.dispatch(procedures["TEST3"])

    time.sleep(30)
    dispatcher.dispatch(procedures["TEST4"])
 
if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    test_vm_commands()