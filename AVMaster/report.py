__author__ = 'fabrizio'

import logging
import pickle
import yaml

class Report:
    c_sent = {}
    c_received = {}

    def init(self, procedure):
        self.name = procedure.name

    # arriva pulito
    def sent(self, av, command):
        logging.debug("sent: %s (%s)" % (av, command))
        Report.c_sent[av]=str(command)
        self.dump()

    # arriva pulito
    def received(self, av, command):
        logging.debug("received: %s (%s)" % (av, command))
        if av not in Report.c_received:
            Report.c_received[av] = []
        Report.c_received[av].append(str(command))
        self.dump()

    def dump(self):
        f=open("report.%s.log" % self.name, "w+")
        rep = {}

        for k in self.c_received.keys():
            try:
                rep[k]={"RECEIVED" : self.c_received[k], "LAST_SENT" : self.c_sent.get(k,"") }
                rep["LAST_RECEIVED": (k, self.c_received[k][-1]) ]
            except:
                pass

        f.write(yaml.dump(rep, default_flow_style=False, indent=4))
