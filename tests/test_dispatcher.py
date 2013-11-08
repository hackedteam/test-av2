import sys, os
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import logging, logging.config
from multiprocessing import Pool
import threading

from AVCommon.procedure import Procedure
from AVCommon.mq import MQStar
from AVMaster.dispatcher import Dispatcher
from AVMaster import vm_manager

from AVAgent import av_agent

def test_dispatcher_server():
    host = "localhost"

    vms = ["noav", "zenovm"]

    #test = Procedure("TEST", ["BEGIN", ("EVAL_SERVER",'self.vm'), "END"])
    test = Procedure("TEST", [("EVAL_SERVER",'self.vm')])

    host = "localhost"
    mq = MQStar(host)
    mq.clean()

    #istanzia n client e manda delle procedure.

    vm_manager.vm_conf_file = "../AVMaster/conf/vms.cfg"
    dispatcher = Dispatcher(mq, vms)
    dispatcher.dispatch(test)

def test_dispatcher_client():
    host = "localhost"

    vms = [ "testvm_%d" % i for i in range(10) ]

    test = Procedure("TEST", [ "START_AGENT", ("EVAL_CLIENT",'self.vm'), {   'COMMAND_CLIENT': [{   'BUILD': [   'windows',
                                                           'whatever']}]}, "STOP_AGENT"])

    host = "localhost"
    mq = MQStar(host)
    mq.clean()

    logging.debug("MQ session: %s" % mq.session)

    #istanzia n client e manda delle procedure.

    vm_manager.vm_conf_file = "../AVMaster/conf/vms.cfg"

    # dispatcher, inoltra e riceve i comandi della procedura test sulle vm
    dispatcher = Dispatcher(mq, vms)
    thread = threading.Thread(target=dispatcher.dispatch, args=(test["TEST"],))
    thread.start()

    # i client vengono eseguiti asincronicamente e comunicano tramite redis al server
    pool = Pool(len(vms))
    r = pool.map_async(av_agent.start_agent, ( (v, host, mq.session) for v in vms) )
    r.get() #notare che i results dei client non ci interessano, viaggia tutto su channel/command.

    # chiusura del server
    thread.join()


if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    #test_dispatcher_server()
    test_dispatcher_client()
