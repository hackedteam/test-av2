import sys
import os
import logging
import logging.config
from time import sleep

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVMaster.vm_manager import VMManager


def test_instance():
    vm = VMManager()
    assert vm

def test_up_and_down():
    vmm = VMManager("../AVMaster/conf/vms.cfg")
    logging.info( "TEST VMManager")
    #vms=["zenovm", "noav"]
    vms = ["noav"]

    logging.info( "Testing existent methods")
    for vm in vms:
        if not vmm.execute(vm, "is_powered_on"):
            logging.debug("powering on %s" % vm)
            vmm.execute(vm, "startup")

    for vm in vms:
        while not vmm.execute(vm, "is_powered_on") :
            logging.debug( "sleeping 5 secs waiting for avg")
            sleep(5)

    for vm in vms:
        assert vmm.execute(vm, "is_powered_on")

    for vm in vms:
        vmm.execute(vm, "shutdown")

    for vm in vms:
        while vmm.execute(vm, "is_powered_on"):
            logging.debug( "sleeping 5 secs waiting for avg")
            sleep(5)

    for vm in vms:
        assert vmm.execute(vm, "is_powered_off")

    logging.info( "Testing non existent methods")
    for vm in vms:
        assert vmm.execute(vm, "this_method_doesnt_exists") is False

if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    test_instance()
    test_up_and_down()
