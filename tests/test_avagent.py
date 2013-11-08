__author__ = 'fabrizio'

import sys, os
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import logging, logging.config
from multiprocessing import Pool, Process

from AVCommon.procedure import Procedure
from AVCommon.mq import MQStar
from AVMaster.dispatcher import Dispatcher
from AVMaster import vm_manager

from AVAgent import av_agent

def test_avagent():
    host = "localhost"

    vms = [ "testvm_%d" % i for i in range(10) ]

    test = Procedure("TEST", ["BEGIN", "START_AGENT", ("EVAL_CLIENT",'self.vm'), "STOP_AGENT", "END"])

    host = "localhost"
    mq = MQStar(host)
    mq.clean()

    logging.debug("MQ session: %s" % mq.session)

    agent = av_agent.AVAgent("test_1", session=mq.session)
    assert agent

    #agent.start_agent()

if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    #test_dispatcher_server()
    test_avagent()
