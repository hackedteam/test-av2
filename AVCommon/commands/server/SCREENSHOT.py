import os
import sys
from AVCommon.logger import logging
import time


def execute(vm, img_path):
    """ server side """
    from AVMaster import vm_manager

    logging.debug("    CS Execute")
    assert vm, "null vm"

    basedir = "screenshots"

    if not img_path:
        if not os.path.exists(basedir):
            os.mkdir(basedir)
        img_path = "%s/%s.%s.png" % (basedir, vm, int(time.time()))

    ret = vm_manager.execute(vm, "takeScreenshot", img_path)
    if ret is True:
        #blob = open(img_path).read()
        return ret, img_path
    else:
        return ret, "Screenshot not saved"

