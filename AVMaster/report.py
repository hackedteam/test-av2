__author__ = 'fabrizio'

import logging
import pickle
import yaml
import time

class Report:
    c_sent = {}
    c_received = {}

    test_id =0

    def init(self, procedure):
        self.name = procedure.name
        self.timestamp = int(time.time())

    # arriva pulito
    def sent(self, proc, av, command):
        logging.debug("sent: %s (%s)" % (av, command))
        Report.c_sent[av]=str(command)
        self.dump()

    # arriva pulito
    def received(self, proc, av, command):
        logging.debug("received: %s (%s)" % (av, command))
        if av not in Report.c_received:
            Report.c_received[av] = []
        Report.c_received[av].append(str(command))
        self.db_save(self.test_id, proc, av, command)
        self.dump()

    def dump(self):
        f=open("report.%s.%s.log" % (self.timestamp, self.name), "w+")
        rep = {}

        rep["LAST_RECEIVED"] = []
        for k in self.c_received.keys():
            try:
                rep[k]={"RECEIVED" : self.c_received[k], "LAST_SENT" : self.c_sent.get(k,"") }
                rep["LAST_RECEIVED"].append( {k: self.c_received[k][-1]} )
            except:
                pass

        f.write(yaml.dump(rep, default_flow_style=False, indent=4))
