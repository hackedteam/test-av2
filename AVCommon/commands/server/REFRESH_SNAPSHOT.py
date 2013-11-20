import os
import sys
import logging

def execute(vm, args):
    """ server side """

    from AVMaster import vm_manager

    logging.debug("    CS Execute REFRESH SNAPSHOT")
    assert vm, "null vm"

    # TODO: check
    vm_manager.execute(vm, "refreshSnapshot")
    return True, "Snapshot refreshed for VM"


