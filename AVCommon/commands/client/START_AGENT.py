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
    processes = vm_manager.execute(vm, "list_processes")
    python = [ p for p in processes if "python" in p['cmd_line'] ]
    logging.debug("processes python: %s" % python)


    if not python:
        raise RuntimeError("Error executing command av_agent")


def on_answer(vm, success, answer):
    """ server side """
    pass


def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    START AGENT")
    assert vm, "null vm"

    return True, "AGENT STARTED"


