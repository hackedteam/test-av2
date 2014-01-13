__author__ = 'zeno'


import os
from AVCommon.logger import logging

from AVCommon.procedure import Procedure
from AVCommon.mq import MQStar
from AVMaster.dispatcher import Dispatcher
from AVMaster import vm_manager

from AVMaster import report


def test_report_extract():
    logging.debug("dir: %s" % os.getcwd())
    r = report.restore("report.CHECK_ELITE.log")

    s = report.summary()
    logging.debug(s)

    assert r.name
    assert r.c_received
    assert r.c_sent

    report.clean()


def test_report_load():
    r = report.restore("report.UPDATE_FAST.log")

    r2 = report.Report()
    assert r.c_sent == r2.c_sent

    assert r.name
    assert r.c_received
    assert r.c_sent

    report.clean()

def test_report_meta():
    yaml = """

P1:
    - SLEEP: 1

P2:
    - SLEEP

P3:
    - SLEEP: 2

P4:
    - SLEEP


TEST_REPORT:
    - VM: [noav,zenoav]
    - SET_SERVER:
        mail_recipients: [zeno@hackingteam.it]
    - REPORT:
        - P1: ["AVtest", "MyCase"]
        - P2: ["AVtest", "MyOtherCase", INVERSE ]
        - P3
        - P4
"""
    procedures = Procedure.load_from_yaml(yaml)

    vms = ["noav", "zenovm"]
    #vms = ["noav"]
    redis_host = "localhost"
    mq = MQStar(redis_host)
    mq.clean()

    vm_manager.vm_conf_file = "../AVMaster/conf/vms.cfg"
    dispatcher = Dispatcher(mq, vms)

    logging.info("STARTING TEST REPORT")
    dispatcher.dispatch(procedures["TEST_REPORT"])
    logging.info("STOPPING TEST REPORT")

    r = report.Report()
    #report.finish()

    assert r
    assert len(r.c_received) == len(vms)
    assert len(r.c_sent) == len(vms)
    assert len(r.current_procedure) == len(vms)
    assert len(r.c_received) == len(vms), len(r.c_received)
    for vm in vms:
        assert vm in r.c_received
        assert len(r.c_received[vm]) >= 18


    #logging.debug("Report: %s" % r )


if __name__=="__main__":
    #test_report_extract()
    #test_report_load()
    #logging.init()
    test_report_meta()