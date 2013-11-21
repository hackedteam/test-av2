import logging
import time


def on_init(vm, args):
    """ server side """
    from AVMaster import vm_manager

    cmd = "c:\\python27\\python.exe"
    arg = ["C:\\AVTest\\AVAgent\\av_agent.py", "-m", vm, "-s", "SESSION1", "-d", "10.0.20.1"]
    ret = vm_manager.execute(vm, "executeCmd", cmd, arg, 40, True, True)

    logging.debug("execution: %s" % ret)

    time.sleep(5)
    ret = vm_manager.execute(vm, "list_processes")
    logging.debug("processes: %s" % ret)

    #if ret != 1:
    #    raise RuntimeError("Error executing command, result: %s" % ret)


def on_answer(vm, success, answer):
    """ server side """
    pass


def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    START AGENT")
    assert vm, "null vm"

    return True, "AGENT STARTED"


