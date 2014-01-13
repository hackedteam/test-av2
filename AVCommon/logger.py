__author__ = 'fabrizio'

import logging as l
#import logging.config
import yaml
import os
import time

logdir_base = "../logs"
logdir = logdir_base

if not os.path.exists(logdir):
    os.mkdir(logdir)

#with open("../AVCommon/logging.yml") as o:
#    logging.config.dictConfig(yaml.load(o))

def init(report = ""):
    print "init"

    if report:
        logdir = "%s/%s" % (logdir_base, report)
        logging = setFileLogger(logdir)
    else:
        logging = setStreamLogger()

    globals()["logging"] = logging

def setStreamLogger():
    # TODO
    ts = time.strftime("%y%m%d-%H%M%S", time.localtime(time.time()))

    FORMAT= '%(asctime)s %(levelname)7s %(filename)14s:%(lineno)3d| %(message)s'
    DATE_FORMAT= '%Y%m%d %H%M%S'

    formatter = l.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)

    handler = l.StreamHandler()
    handler.setFormatter(formatter)

    logger = l.getLogger('AVM')
    logger.setLevel(l.DEBUG)
    logger.addHandler(handler)

    return logger

def setFileLogger(report_dir):
    # TODO
    ts = time.strftime("%y%m%d-%H%M%S", time.localtime(time.time()))

    FORMAT= '%(asctime)s %(levelname)7s %(filename)14s:%(lineno)3d| %(message)s'
    DATE_FORMAT= '%Y%m%d %H%M%S'

    formatter = l.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
    #filename = "%s/avmonitor-%s.log" % (logdir, ts)

    if not os.path.exists(report_dir):
        os.mkdir(report_dir)

    #filename  = "%s/avmonitor-%s.log" % (report_dir, ts)
    filename  = "%s/avmonitor.log" % (report_dir)
    file_handler = l.FileHandler(filename)
    file_handler.setLevel(l.DEBUG)
    file_handler.setFormatter(formatter)

    handler = l.StreamHandler()
    handler.setFormatter(formatter)

    logger = l.getLogger('AVM')
    logger.setLevel(l.DEBUG)

    logger.addHandler(handler)
    logger.addHandler(file_handler)

    logger.info("START")

    return logger

init()
logging.info("START LOGGING")