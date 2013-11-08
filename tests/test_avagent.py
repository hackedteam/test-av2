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

class Report:
    c_sent = {}
    c_received = {}
    def sent(self, av, command):
        if av not in self.c_sent:
            self.c_sent[av] = []
        self.c_sent[av].append(command)
    def received(self, av, command):
        if av not in self.c_received:
            self.c_received[av] = []
        self.c_received[av].append(command)

def test_avagent_create():
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

def test_avagent_get_set():
    host = "localhost"

    vms = [ "testvm_%d" % i for i in range(1) ]

    #command_client={   'COMMAND_CLIENT': [{   'SET': [   'windows'                                 'whatever']}]}

    procedure = """
TEST:
    - START_AGENT
    - COMMAND_CLIENT:
        - SET: pippo=franco
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
    report= Report()

    # dispatcher, inoltra e riceve i comandi della procedura test sulle vm
    dispatcher = Dispatcher(mq, vms, report)
    p = Process(target=dispatcher.dispatch, args=(test["TEST"],))
    p.start()

    # i client vengono eseguiti asincronicamente e comunicano tramite redis al server
    pool = Pool(len(vms))
    r = pool.map_async(av_agent.start_agent, ( (v, host, mq.session) for v in vms) )
    r.get() #notare che i results dei client non ci interessano, viaggia tutto su channel/command.

    # chiusura del server
    p.join()

    logging.debug(report)
    logging.debug("sent: %s" % report.c_sent)
    logging.debug("received: %s" % report.c_received)

if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    #test_dispatcher_server()
    test_avagent_get_set()
