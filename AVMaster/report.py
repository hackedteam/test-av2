__author__ = 'fabrizio'

import os
from AVCommon.logger import logging
from AVCommon import logger
import pickle
import yaml
import time
import random
import uuid
import ast

report = None
from AVCommon.singleton import Singleton

class Cmd:
    def __init__(self, cmd):
        res = [ s.strip() for s in cmd.split(',', 4)]
        self.name, self.success, self.ts, self.args, self.result = res

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

        self.timestamp = time.strftime("%y%m%d-%H%M%S", time.localtime(time.time()))

        #self.timestamp = int(time.time())

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
    dump()

def finish():
    logging.debug("report finish")
    #dump()

def is_success(cmd):

    c = Cmd(cmd)
    return c.success

def get_result(received, sent):
    report = Report()

    if not is_success(sent):
        return [ False, sent ]

    builds = [ b for b in received if b.startswith("BUILD")]
    failed = [ b for b in builds if   "+ ERROR" in b or "+ FAILED" in b ]
    if failed:
        return [False, failed[-1]]
    if builds:
        last = builds[-1]
        return [True, last]
    else:
        last = received[-1]
        return [is_success(last), last]

def set_procedure(vm, proc_name):
    report = Report()

    assert vm in report.c_received, "%s not in %s" % (vm, report.c_received)

    if vm in report.current_procedure.keys():
        proc = report.current_procedure[vm]
        if proc not in report.reports.keys():
            report.reports[proc]=[]

        res = get_result(report.c_received[vm], report.c_sent[vm])
        logging.debug("adding %s/%s: %s" % (proc, vm, str(res)))

        report.reports[proc].append({ vm: res })

        # qui si deve salvare il record: t_id = report.test_id, name = vm,  kind = proc, result = res

    report.current_procedure[vm] = proc_name
    assert vm in report.current_procedure.keys(), "%s not in %s" % (vm, report.current_procedure.keys())

def report():
    report = Report()
    report.vm = {}

    summary = ""
    for vm in report.c_received.keys():
        report.vm[vm] = []
        current_proc = None
        summary += "%s\n" % vm
        for c in report.c_received[vm]:
            cmd = Cmd(c)

            if cmd.name == "REPORT_KIND":
                current_proc = cmd.args
                report.vm[vm].append(current_proc)
                summary += "  %s\n" % current_proc
            else:
                if current_proc:
                    if cmd.success == 'False':
                        summary+="    %s\n" % c
                    elif cmd.name=="BUILD" and cmd.success == 'None':
                        check = ['+ ERROR','+ FAILED']
                        errors = any([ s in c for s in check ])
                        if errors:
                            summary+="    %s\n" % (c)
    return summary


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

    f=open("%s/report.%s.%s.log" % (logger.logdir, report.timestamp, report.name), "w+")
    f.write(yaml.dump(report, default_flow_style=False, indent=4))

def restore(file_name):
    #report = Report()
    logging.debug("dir: %s list: %s" % (os.getcwd(), os.listdir(".")))

    assert os.path.exists(file_name)

    f = open(file_name)
    lines = []
    while True:
        l = f.readline()
        if not l:
            break
        if "lambda" in l:
            continue
        lines.append(l)

    y = "".join(lines)

    r = yaml.load(y)
    Report().init(r)
    return r
