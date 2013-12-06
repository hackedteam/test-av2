import logging
import time


def on_init(protocol, args):
    """ server side """
    from AVMaster import vm_manager

    vm, mq = protocol.vm, protocol.mq
    cmd = "c:\\python27\\python.exe"

    if mq.host == "localhost":
        redis = "10.0.20.1"
    else:
        redis = mq.host

    arg = ["C:\\AVTest\\AVAgent\\av_agent.py", "-m", vm, "-s", mq.session, "-d", redis]
    ret = vm_manager.execute(vm, "executeCmd", cmd, arg, 40, True, True)

    logging.debug("execution: %s" % ret)

    for i in range(5):
        time.sleep(10)
        processes = vm_manager.execute(vm, "list_processes")
        if not processes:
            logging.debug("%s: null list_processes" % vm)
            continue
        python = [ p for p in processes if "python" in p['cmd_line'] ]
        logging.debug("processes python: %s" % python)
        if python:
            return True

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


