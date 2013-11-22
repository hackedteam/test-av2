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
        logging.debug("sent: %s, %s" % (av, command))
        if av not in Report.c_sent:
            Report.c_sent[av] = []
        Report.c_sent[av].append(str(command))

    # arriva pulito
    def received(self, av, command):
        logging.debug("received: %s, %s" % (av, command))
        if av not in Report.c_received:
            Report.c_received[av] = []
        Report.c_received[av].append(str(command))

    def dump(self):
        f=open("report.%s.log" % self.name, "w+")
        f.write(yaml.dump(self.c_received), default_flow_style=False)