import os
import sys
import argparse

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import logging

from AVCommon.procedure import Procedure
from AVMaster.dispatcher import Dispatcher
from AVCommon.mq import MQStar
from AVCommon import command

class AVMaster():
    """docstring for Master"""

    def __init__(self, args):
        self.args = args
        self.vm_names = args.vm.split(',')
        self.procedure = args.procedure.upper()
        command.init("AVCommon")

    def start(self):

        procedures = Procedure.load_from_file("../AVCommon/procedures.yaml")
        proc = procedures[self.procedure]
        assert proc, "cannot find the specified procedure: %s" % self.procedure

        mq = MQStar(self.args.redis, self.args.session)
        if self.args.clean:
            mq.clean()

        logging.info("mq session: %s" % mq.session)

        dispatcher = Dispatcher(mq, self.vm_names)

        dispatcher.dispatch(proc)

    def on_finished(self, vm):
        pass


def main():
    parser = argparse.ArgumentParser(description='AVMonitor master.')

    parser.add_argument('-m', '--vm', required=True,
                        help="Virtual Machines comma separated on which executing the operation")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Verbose")
    parser.add_argument('-r', '--procedure', type=str, default=False, required=True,
                        help="Procedure to execute")
    parser.add_argument('-p', '--pool', type=int, required=False, default=8,
                        help="This is the number of parallel process (default 8)")
    parser.add_argument('-d', '--redis', default="localhost",
                        help="redis host")
    parser.add_argument('-c', '--clean', default=False,
                        help="clean redis mq")
    parser.add_argument('-s', '--session', default=False,
                        help="session redis mq ")

    args = parser.parse_args()

    logging.debug(args)
    master = AVMaster(args)
    master.start()


if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    main()
