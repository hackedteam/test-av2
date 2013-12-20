__author__ = 'fabrizio'

import sys, os
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVCommon.logger import logging
from multiprocessing import Pool, Process
import threading

from AVCommon.procedure import Procedure
from AVCommon.mq import MQStar
from AVMaster.dispatcher import Dispatcher
from AVMaster import vm_manager

from AVAgent import av_agent

from AVMaster import report
from AVCommon import command

import time

def on_init(vm, args):
    pass

command.init()
command.known_commands['START_AGENT'].on_init= on_init

def test_avagent_create():
    host = "localhost"

    vms = [ "testvm_%d" % i for i in range(10) ]



    test = Procedure("TEST", ["BEGIN", "START_AGENT", ("EVAL_CLIENT", None, 'self.vm'), "STOP_AGENT", "END"])

    host = "localhost"
    mq = MQStar(host)
    mq.clean()

    logging.debug("MQ session: %s" % mq.session)

    agent = av_agent.AVAgent("test_1", session=mq.session)
    assert agent

    #agent.start_agent()

def test_avagent_get_set():
    host = "localhost"

    vms = [ "testvm_%d" % i for i in range(100) ]

    #command_client={   'COMMAND_CLIENT': [{   'SET': [   'windows'                                 'whatever']}]}

    procedure = """
TEST:
    - START_AGENT
    - SET: {pippo: franco}
    - SET:
        backend: 192.168.100.201
        frontend: 172.20.100.204
        redis: 10.0.20.1
    - SET:
        android:
          binary: {admin: false, demo: true}
          melt: {}
          platform: android
          sign: {}
    - GET: pippo
    - STOP_AGENT
"""

    test = Procedure.load_from_yaml(procedure)

    host = "localhost"
    mq = MQStar(host)
    mq.clean()

    logging.debug("MQ session: %s" % mq.session)

    #istanzia n client e manda delle procedure.

    vm_manager.vm_conf_file = "../AVMaster/conf/vms.cfg"

    # dispatcher, inoltra e riceve i comandi della procedura test sulle vm
    dispatcher = Dispatcher(mq, vms, timeout = 10)
    thread = threading.Thread(target=dispatcher.dispatch, args=(test["TEST"],))
    thread.start()
    #p = Process(target=dispatcher.dispatch, args=(test["TEST"],))
    #p.start()

    # i client vengono eseguiti asincronicamente e comunicano tramite redis al server
    #pool = Pool(len(vms))
    #r = pool.map_async(av_agent.start_agent, ( (v, host, mq.session) for v in vms) )
    #r.get() #notare che i results dei client non ci interessano, viaggia tutto su channel/command.

    for v in vms:
        t = threading.Thread(target=av_agent.start_agent_args,  args=(v, host, mq.session)  )
        t.start()
        #p = Process(target=av_agent.start_agent, args=( tuple([v, host, mq.session,])))
        #p.start()

    # chiusura del server
    #p.join()
    thread.join()

    r = report.Report()
    logging.debug("sent: %s" % r.c_sent)
    logging.debug("received: %s" % r.c_received)

if __name__ == '__main__':

    #test_dispatcher_server()
    test_avagent_get_set()
