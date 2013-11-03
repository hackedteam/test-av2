__author__ = 'fabrizio'
import os, sys
import logging
import logging.config

def test_import():
    prev = os.path.join(os.getcwd(), "..")
    if not prev in sys.path:
        sys.path.append(prev)


    sys.path.append("../AVCommon")
    import AVCommon
    from AVCommon import MQ

if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
