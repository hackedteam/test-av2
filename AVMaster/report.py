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
    def init(self, o):
        self.c_sent = o.c_sent
        self.c_received = o.c_received

        self.test_id = o.test_id
        self.timestamp = o.timestamp

        self.reports = o.reports
        self.current_procedure = o.current_procedure
        self.procedures = o.procedures
        self.name = o.name

    def __init__(self):
        self.c_sent = {}
        self.c_received = {}

        self.test_id = str(uuid.uuid1())
        self.timestamp = int(time.time())

        self.reports = {} # proc is the key
        self.current_procedure = {} # vm is the key
        self.procedures = []
        self.name = ""


def init(name):
    report = Report()
    report.name = name

def clean():
    Report().__init__()

def end(vm):
    report = Report()
    #
    logging.debug("setting end to %s" % vm)
    set_procedure(vm, None)

def finish():
    logging.debug("report finish")
    dump()

def get_result(received):
    report = Report()

    builds = [ b for b in received if b.startswith("BUILD")]
    failed = [ b for b in builds if   "+ ERROR" in b or "+ FAILED" in b ]
    if failed:
        return [False, failed[-1]]
    if builds:
        last = builds[-1]
        return [True, last]
    else:
        return [True, received[-1]]

def set_procedure(vm, proc_name):
    report = Report()

    assert vm in report.c_received, "%s not in %s" % (vm, report.c_received)

    if vm in report.current_procedure.keys():
        proc = report.current_procedure[vm]
        if proc not in report.reports.keys():
            report.reports[proc]=[]

        res = get_result(report.c_received[vm])
        logging.debug("adding %s/%s: %s" % (proc, vm, str(res)))

        report.reports[proc].append({ vm: res })

        # qui si deve salvare il record: t_id = report.test_id, name = vm,  kind = proc, result = res

    report.current_procedure[vm] = proc_name
    assert vm in report.current_procedure.keys(), "%s not in %s" % (vm, report.current_procedure.keys())

# arriva pulito
def sent(av, command):
    report = Report()

    assert isinstance( av, str)
    logging.debug("sent (%s): %s (%s)" % (report.current_procedure.get(av,""), av, command))
    report.c_sent[av]=str(command)
    dump()

# arriva pulito
def received(av, command):
    report = Report()

    assert isinstance( av, str)

    logging.debug("received (%s): %s (%s)" % (report.current_procedure.get(av,""), av, command))
    if av not in report.c_received:
        report.c_received[av] = []
    report.c_received[av].append(str(command))
    #db_save(test_id, proc, av, command)
    dump()

def dump():
    report = Report()

    f=open("report.%s.%s.log" % (report.timestamp, report.name), "w+")
    f.write(yaml.dump(report, default_flow_style=False, indent=4))

def restore(file_name):
    #report = Report()
    f = open(file_name)

    r = yaml.load(f)
    Report().init(r)
    return r
