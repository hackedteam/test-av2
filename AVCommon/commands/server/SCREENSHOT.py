import os
import sys
import logging


def execute(vm, img_path):
    """ server side """
    from AVMaster import vm_manager

    logging.debug("    CS Execute")
    assert vm, "null vm"
    #img_path = "/tmp/img_path.png"

    ret = vm_manager.execute(vm, "takeScreenshot", img_path)
    if ret is True:
        return ret, "Screenshot saved on file %s" % img_path
    else:
        return ret, "Screenshot not saved"

