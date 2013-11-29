__author__ = 'fabrizio'

import logging
import pickle
import yaml
import time
import random
import uuid

report = None
from AVCommon.singleton import Singleton

@Singleton
class Report:
    def __init__(self):
        self.c_sent = {}
        self.c_received = {}

        self.test_id = str(uuid.uuid1())
        self.timestamp = int(time.time())

        self.reports = {} # proc is the key
        self.current_procedure = {} # vm is the key
        self.procedures = []


def init(name):
    report = Report.Instance()
    report.name = name

def end():
    global report
    for vm in report.current_procedure.keys():
        set_procedure(vm, "END")


def get_result(received):
    report = Report.Instance()

    builds = [ b for b in received if b.startswith("BUILD")]
    failed = [ b for b in builds if   "+ ERROR" in b or "+ FAILED" in b ]
    if failed:
        return [False, failed[-1]]
    if builds:
        last = builds[-1]
        return [ True, last ]
    else:
        return [True, received[-1]]

def set_procedure(vm, proc_name):
    report = Report.Instance()

    if vm in report.current_procedure.keys():
        if vm in report.c_received:
            proc = report.current_procedure[vm]
            if proc not in report.reports.keys():
                report.reports[proc]=[]
            report.reports[proc].append({ vm: get_result(report.c_received[vm]) })
        else:
            logging.debug("no vm in report.c_received")
    else:
        logging.debug("no vm in report.current_procedure")

    report.current_procedure[vm] = proc_name

# arriva pulito
def sent(av, command):
    report = Report.Instance()

    assert isinstance( av, str)
    logging.debug("sent (%s): %s (%s)" % (report.current_procedure.get(av,""), av, command))
    report.c_sent[av]=str(command)
    dump()

# arriva pulito
def received(av, command):
    report = Report.Instance()

    assert isinstance( av, str)

    logging.debug("received (%s): %s (%s)" % (report.current_procedure.get(av,""), av, command))
    if av not in report.c_received:
        report.c_received[av] = []
    report.c_received[av].append(str(command))
    #db_save(test_id, proc, av, command)
    dump()

def dump():
    report = Report.Instance()

    f=open("report.%s.%s.log" % (report.timestamp, report.name), "w+")
    f.write(yaml.dump(report, default_flow_style=False, indent=4))

def restore(file_name):
    report = Report.Instance()

    f = open(file_name  )
    report = yaml.load(f)
