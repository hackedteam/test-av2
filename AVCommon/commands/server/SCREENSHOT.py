import os
import sys
import logging
import time

def execute(vm, img_path):
    """ server side """
    from AVMaster import vm_manager

    logging.debug("    CS Execute")
    assert vm, "null vm"

    if not img_path:
        try:
            os.mkdir("screenshot")
        except:
            pass
        img_path = "screenshot/%s.%s.png" % (vm, int(time.time()))

    ret = vm_manager.execute(vm, "takeScreenshot", img_path)
    if ret is True:
        blob = open(img_path).read()
        return ret, blob
    else:
        return ret, "Screenshot not saved"

