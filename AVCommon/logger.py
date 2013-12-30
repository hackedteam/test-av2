__author__ = 'fabrizio'

import logging
import logging.config
import yaml
import os
import time

logdir = "../logs"

if not os.path.exists(logdir):
    os.mkdir(logdir)

with open("../AVCommon/logging.yml") as o:
    logging.config.dictConfig(yaml.load(o))

def setFileLogger():
    # TODO
    ts = time.strftime("%y%m%d-%H%M%S", time.localtime(time.time()))

    filename = "%s/avmonitor-%s.log" % (logdir, ts)
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.DEBUG)

    file_handler.setFormatter(logging.formatters[0])
    logging.root.addHandler(file_handler)

logging.info("START LOGGING")