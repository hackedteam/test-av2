__author__ = 'zeno'

import os
import sys
import argparse
import glob

sys.path.append(os.path.split(os.getcwd())[0])

from AVCommon import logger
import time


def main():
    parser = argparse.ArgumentParser(description='AVMonitor master.')

    parser.add_argument('-m', '--vm', required=False, default="",
                        help="Virtual Machines comma separated on which executing the operation")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Verbose")
    parser.add_argument('-r', '--procedure', type=str, default=False, required=True,
                        help="Procedure to execute")
    parser.add_argument('-p', '--pool', type=int, required=False, default=6,
                        help="This is the number of parallel process (default 6)")
    parser.add_argument('-d', '--redis', default="localhost",
                        help="redis host")
    parser.add_argument('-c', '--clean', default=False, action='store_true',
                        help="clean redis mq")
    parser.add_argument('-s', '--session', default="dsession",
                        help="session redis mq ")
    parser.add_argument('-e', '--report', type=str, default="")

    args = parser.parse_args()

    if args.report:
        report=args.report
    else:
        report =  time.strftime("%y%m%d", time.localtime(time.time()))

    logger.init(report)

    from AVCommon.logger import logging
    globals()['logging']=logging

    logging.debug(args)
    from av_master import AVMaster
    master = AVMaster(args)
    master.start()


if __name__ == '__main__':

    #logger=logging.getLogger('root')
    try:
        os.remove("../logs/avmonitor.log")
        os.remove("../logs/avmonitor-info.log")
        os.remove("../logs/avmonitor-error.log")
    except:
        pass
    main()
