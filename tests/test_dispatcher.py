import sys, os
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVCommon.logger import logging
from multiprocessing import Pool
import threading

from AVCommon.procedure import Procedure
from AVCommon.mq import MQStar
from AVMaster.dispatcher import Dispatcher
from AVMaster import vm_manager
from AVMaster import report

from AVAgent import av_agent

def test_dispatcher_server():
    host = "localhost"

    vms = ["noav", "zenovm"]


    host = "localhost"
    mq = MQStar(host)
    mq.clean()

    #istanzia n client e manda delle procedure.
    vm_manager.vm_conf_file = "../AVMaster/conf/vms.cfg"
    dispatcher = Dispatcher(mq, vms)

    test = Procedure("TEST", [("EVAL_SERVER", None, 'vm'), ("SLEEP", None, 10)])

    dispatcher.dispatch(test)

if __name__ == '__main__':

    test_dispatcher_server()

