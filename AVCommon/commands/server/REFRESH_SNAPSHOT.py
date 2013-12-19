import os
import sys
from AVCommon.logger import logging


def execute(vm, protocol, args):
    """ server side """

    from AVMaster import vm_manager

    logging.debug("    CS Execute REFRESH SNAPSHOT")
    assert vm, "null vm"

    # TODO: check
    vm_manager.execute(vm, "refreshSnapshot")
    return True, "Snapshot refreshed for VM"


