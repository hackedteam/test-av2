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

TEST30:
    - BEGIN
    - START_VM
    - END
 
TEST31:
    - BEGIN
    - PUSH
    - EXECUTE_VM: c:\\users\\avtest\\desktop\\pubsub\\started.bat
    - PULL:
        - /tmp/gggg
        - c:\\users\\avtest\\desktop\\ddd.txt
    - SCREENSHOT: /tmp/maggic_path.png
    - PUSH:
        - c:\\users\\avtest\\desktop\\ggggg.txt
        - /tmp/jojojo
    - END
 
TEST32:
    - BEGIN
    - STOP_VM
    - END
 
TEST4:
    - CALL: PSTART
    - SCREENSHOT: /tmp/magic_img_path.png
    - CALL: PSTOP
"""
    procedures = Procedure.load_from_yaml(yaml)
 
    test1 = Procedure.procedures["TEST30"]
    test2 = Procedure.procedures["TEST31"]
    test3 = Procedure.procedures["TEST32"]
 
    #vms = ["noav", "zenovm"]
    vms = ["noav"]
    redis_host = "localhost"
    mq = MQStar(redis_host)
    mq.clean()
 
    vm_manager.vm_conf_file = "../AVMaster/conf/vms.cfg"
    dispatcher = Dispatcher(mq, vms)
    logging.info("STARTING TEST 1")
    dispatcher.dispatch(test1)

    import time
    time.sleep(200)

    logging.info("STARTING TEST 2")
    dispatcher.dispatch(test2)

    time.sleep(30)

    logging.info("STARTING TEST 3")
    dispatcher.dispatch(test3)

#    dispatcher.dispatch(test4)
 
if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    test_vm_commands()