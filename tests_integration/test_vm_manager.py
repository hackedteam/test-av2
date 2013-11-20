import sys
import os
import logging
import logging.config
from time import sleep

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVMaster import vm_manager


def test_instance():
    vm = VMManager()
    assert vm

def test_up_and_down():
#    vmm = VMManager("../AVMaster/conf/vms.cfg")
    vmm = VMManager()
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
    exp = False
    try:
        for vm in vms:
            vmm.execute(vm, "this_method_doesnt_exists")
    except:
        exp = True
    finally:
        assert exp is True

def test_execute():
#    vmm = VMManager()
    logging.info( "TEST VMManager")
    #vms=["zenovm", "noav"]
    vms = ["noav"]
    vm = "noav"
    vm_manager.execute(vm, "executeCmd", "c:/python27/python.exe", [], 40, True, False)


if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
#    test_instance()
#    test_up_and_down()
    test_execute()
