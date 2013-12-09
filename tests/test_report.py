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
    assert r.name == "CHECK_ELITE"
    assert r.c_received
    assert r.c_sent

    s = report.report()
    logging.debug(s)

    report.clean()


def test_report_load():
    r = report.restore("report.UPDATE_FAST.log")

    r2 = report.Report()
    assert r.c_sent == r2.c_sent

    assert r.name == "TEST_DAILY"
    assert r.c_received
    assert r.c_sent

    report.clean()

def test_report_meta():
    yaml = """

P1:
    - SLEEP: 1

P2:
    - SLEEP: 2

P3:
    - SLEEP: 3

TEST_REPORT:
    - VM: [noav,zenoav]
    - REPORT:
        - P1
        - P2
        - P3
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

    assert r
    assert len(r.c_received) == len(vms)
    assert len(r.c_sent) == len(vms)
    assert len(r.current_procedure) == len(vms)
    assert len(r.reports) == 3

    #logging.debug("Report: %s" % r )


if __name__=="__main__":

    test_report_extract()
    test_report_load()
    test_report_meta()