__author__ = 'zeno'

import sys, os
from AVCommon.logger import logging

def test_import_avcommon():
    sys.path.append(os.path.split(os.getcwd())[0])
    sys.path.append(os.getcwd())
    #sys.path.append("/Users/zeno/HT/RCSAVTest/")
    logging.debug("cwd: %s" % os.getcwd())
    logging.debug(sys.path)

    import AVCommon

if __name__ == "__main__":

    test_import_avcommon()
