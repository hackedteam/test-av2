__author__ = 'fabrizio'
 
import sys
import os
from time import sleep
#import time

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVCommon.logger import logging
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
        - [/tmp/gggg]
        - c:\\users\\avtest\\desktop
    - SCREENSHOT: /tmp/maggic_path.png

TEST3:
    - PUSH:
        - [gggg, jojojo]
        - /tmp
        - c:\\users\\avtest\\desktop
    - PUSH:
        - [AVAgent/av_agent.py, AVAgent/build.py, AVAgent/package.py, AVAgent/rcs_client.py,
            AVCommon/commands/START_AGENT.py, AVCommon/commands/STOP_AGENT.py,
            AVCommon/commands/BUILD.py, AVCommon/commands/GET.py, AVCommon/commands/SET.py]
        - /home/olli/AVTest
        - c:\\AVTest
    - PULL:
        - [gggg, jojojo]
        - c:\\users\\avtest\\desktop
        - /tmp/cpl
 
TEST4:
    - START_VM
    - SCREENSHOT: /tmp/magic_img_path.png
    - STOP_VM

TEST5:
    - PUSH:
        - [AVCommon/commands/client/*.py]
        - /home/olli/AVTest
        - C:\\AVTest
    - PUSH:
        - [AVAgent/*.py]
        - /home/olli/AVTest
        - C:\\AVTest


UPLOAD_AGENT:
    - PUSH:
        - [AVAgent/av_agent.py, AVAgent/build.py, AVAgent/package.py, AVAgent/rcs_client.py, AVCommon/commands/*.py]
        - /home/olli/AVTest
        - c:\\AVTest

UPDATE:
    - REVERT
    - START_VM
    - SLEEP: 180
    - CALL: UPLOAD_AGENT
    - INTERNET: True
    - SLEEP: 120
    - INTERNET: False
    - STOP_VM
    - START_VM
    - SLEEP: 180
    - STOP_VM
    - REFRESH_SNAPSHOT

ZLEEP:
    - SLEEP: 120

T_IS:
    - CHECK_INFECTION
    - SLEEP:
        - 10
        - 20
    - CHECK_SHUTDOWN
    - SLEEP: 5

TEST_INTERNET:
    - INTERNET: True
    - SLEEP: 15
    - INTERNET: False

TEST_DIR:
    - PUSH:
        - [gigi/gggg]
        - /tmp
        - C:/Users/avtest/Desktop/gigi
    - SLEEP: 10
    - DELETE_DIR: C:/Users/avtest/Desktop/gigi
TEST_DIR_KO:
    - DELETE_DIR: C:/Users/avtest/Desktop/gigiol

TEST_STOP1:
    - STOP_VM: 60
TEST_STOP:
    - STOP_VM
"""
    procedures = Procedure.load_from_yaml(yaml)
 
    #vms = ["noav", "zenovm"]
    vms = ["zenoav"]
    redis_host = "localhost"
    mq = MQStar(redis_host)
    mq.clean()
 
    vm_manager.vm_conf_file = "../AVMaster/conf/vms.cfg"
    dispatcher = Dispatcher(mq, vms)
    '''
    logging.info("STARTING TEST 1")
    dispatcher.dispatch(procedures["TEST1"])

    import time
    time.sleep(200)

    logging.info("STARTING TEST 2")
    dispatcher.dispatch(procedures["TEST2"])

    time.sleep(30)

    dispatcher.dispatch(procedures["TEST3"])
    time.sleep(30)

    logging.info("STARTING TEST UPDATE PROCEDURE")
    dispatcher.dispatch(procedures["UPDATE"])
    '''
    logging.info("STARTING TEST 5")
    dispatcher.dispatch(procedures["TEST_STOP"])

if __name__ == '__main__':

    test_vm_commands()