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
from AVCommon import config
from AVCommon import command
from collections import OrderedDict
from AVCommon.helper import red

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
        self.c_sent = OrderedDict()
        self.c_received = OrderedDict()

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
    logging.debug("setting end to %s" % vm)
    set_procedure(vm, None)
    dump()

def finish():
    logging.debug("report finish")
    #dump()

def set_procedure(vm, proc_name):
    report = Report()

    assert vm in report.c_received, "%s not in %s" % (vm, report.c_received)

    if vm in report.current_procedure.keys():
        proc = report.current_procedure[vm]

        # qui si deve salvare il record: t_id = report.test_id, name = vm,  kind = proc, result = res

    report.current_procedure[vm] = proc_name
    assert vm in report.current_procedure.keys(), "%s not in %s" % (vm, report.current_procedure.keys())

def summary():
    report = Report()
    report.vm = {}

    summary = ""
    for vm in report.c_received.keys():
        report.vm[vm] = []
        current_proc = None
        summary += "%s\n" % vm
        for cmd in report.c_received[vm]:
            #cmd = Cmd(c)

            if cmd.name == "REPORT_KIND_END":
                current_proc = cmd.args
                report.vm[vm].append(current_proc)
                success = "" if cmd.success else "ERROR"
                summary += "  %s %s\n" % (current_proc, success)
            else:
                if current_proc:
                    if cmd.success == 'False':
                        summary+="    %s\n" % (red(str(cmd)))
                    elif cmd.name=="BUILD" and cmd.success != 'None':
                        #check = ['+ ERROR','+ FAILED']
                        #errors = any([ s in c for s in check ])
                        #if errors:
                        summary+="    %s\n" % (red(str(cmd)))
    return summary

# arriva pulito
def sent(av, cmd):
    report = Report()

    assert isinstance( av, basestring)
    assert isinstance( cmd, command.Command), "type: %s" % type(cmd)

    if config.verbose:
        logging.debug("sent (%s): %s (%s)" % (report.current_procedure.get(av,""), av, cmd))
    report.c_sent[av]=cmd
    dump()

# arriva pulito
def received(av, cmd):
    report = Report()

    assert isinstance( av, basestring)
    assert isinstance( cmd, command.Command), "type: %s" % type(cmd)

    if config.verbose:
        logging.debug("received (%s): %s (%s)" % (report.current_procedure.get(av,""), av, cmd))
    if av not in report.c_received.keys():
        report.c_received[av] = []
    report.c_received[av].append(cmd)
    #db_save(test_id, proc, av, command)
    dump()

def dump():
    report = Report()

    f=open("%s/report.%s.%s.yaml" % (logger.logdir, report.timestamp, report.name), "w+")
    f.write(yaml.dump(report, default_flow_style=False, indent=4))
    f.close()

    f=open("%s/report.%s.%s.log" % (logger.logdir, report.timestamp, report.name), "w+")
    for vm in report.c_received.keys():
        f.write("\n%s:\n" % vm)
        indent = ""
        for v in report.c_received[vm]:
            mark = "  "
            if v.name == "REPORT_KIND_INIT":
                indent = "    "
            elif v.name == "REPORT_KIND_END":
                indent = ""
            if v.success == False:
                mark = "- "
            f.write("%s    %s%s\n" % (indent, mark, red(str(v))))
        f.write("   SENT: %s\n" % report.c_sent[vm])
    f.close()

    r= summary()
    f=open("%s/summary.%s.%s.log" % (logger.logdir, report.timestamp, report.name), "w+")
    f.write(r)

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
