__author__ = 'fabrizio'

import sys, os
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import logging, logging.config
from multiprocessing import Pool, Process
import threading

from AVCommon.procedure import Procedure
from AVCommon.mq import MQStar
from AVMaster.dispatcher import Dispatcher
from AVMaster import vm_manager

from AVAgent import av_agent
from AVMaster.report import Report

def test_avagent_pull():
    host = "localhost"

    vms = [ "testvm_%d" % i for i in range(1) ]

    #command_client={   'COMMAND_CLIENT': [{   'SET': [   'windows'                                 'whatever']}]}

    procedure = """
TEST:
    - START_AGENT
    - SET:
        - [backend, 192.168.100.201]
        - [frontend, 172.20.100.204]
        - [redis, 10.0.20.1]
    - BUILD: [ pull, windows, silent]

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
    thread = threading.Thread(target=dispatcher.dispatch, args=(test["TEST"],))
    thread.start()
    #p = Process(target=dispatcher.dispatch, args=(test["TEST"],))
    #p.start()

    # i client vengono eseguiti asincronicamente e comunicano tramite redis al server
    pool = Pool(len(vms))
    r = pool.map_async(av_agent.start_agent, ( (v, host, mq.session) for v in vms) )
    r.get() #notare che i results dei client non ci interessano, viaggia tutto su channel/command.

    # chiusura del server
    #p.join()
    thread.join()

    logging.debug(dispatcher.report)
    logging.debug("sent: %s" % dispatcher.report.c_sent)
    logging.debug("received: %s" % Report.c_received)

if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    #test_dispatcher_server()
    test_avagent_pull()