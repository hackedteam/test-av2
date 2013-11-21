__author__ = 'fabrizio'

import logging

class Report:
    c_sent = {}
    c_received = {}

    def sent(self, av, command):
        logging.debug("sent: %s, %s" % (av, command))
        if av not in Report.c_sent:
            Report.c_sent[av] = []
        Report.c_sent[av].append(command)

    def received(self, av, command):
        logging.debug("received: %s, %s" % (av, command))
        if av not in Report.c_received:
            Report.c_received[av] = []
        Report.c_received[av].append(command)