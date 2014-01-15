import os
import sys
import argparse
import glob

sys.path.append(os.path.split(os.getcwd())[0])

from AVCommon.logger import logging
from AVCommon import logger

from AVCommon.procedure import Procedure
from dispatcher import Dispatcher
from AVCommon.mq import MQStar
from AVCommon import command

import report
import time

class AVMaster():
    """docstring for Master"""

    def __init__(self, args):
        self.args = args
        self.vm_names = args.vm.split(',')
        self.procedure = args.procedure.upper()
        self.pool = args.pool
        command.init()

    def load_procedures(self):
        if os.path.exists("conf/procedures.yaml"):
            Procedure.load_from_file("conf/procedures.yaml")

        confs = glob.glob("conf/procedures/*.yaml")
        for conf in confs:
            logging.info("Loading conf: %s" % conf)
            Procedure.load_from_file(conf)
        if not Procedure.check():
            raise SyntaxError("Errors in procedures")

    def start(self):
        self.load_procedures()
        proc = Procedure.procedures[self.procedure]
        assert proc, "cannot find the specified procedure: %s" % self.procedure

        # command line vm list overrides procedures.yaml
        if self.vm_names==[''] and proc.command_list and proc.command_list[0].name.startswith("VM"):
            vm_command = proc.command_list.pop(0)
            self.vm_names = vm_command.execute('server', None, vm_command.args)[1]
            logging.info("VM override: %s" % self.vm_names)
        assert self.vm_names, "No VM specified"
        mq = MQStar(self.args.redis, self.args.session)
        if self.args.clean:
            logging.warn("cleaning mq")
            mq.clean()

        logging.info("mq session: %s" % mq.session)

        dispatcher = Dispatcher(mq, self.vm_names)
        dispatcher.dispatch(proc, pool = self.pool)

    def on_finished(self, vm):
        pass