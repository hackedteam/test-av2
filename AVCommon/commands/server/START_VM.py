import os
import sys
from AVCommon.logger import logging
from time import sleep
from AVCommon import mq
from AVCommon import helper

def get_status(vm):
    from AVMaster import vm_manager
    # [19/12/13 11:09:23] Seppia: pid=1432, owner=WIN7-NOAV\avtest, cmd=vmtoolsd.exe
    # pid=1776, owner=NT AUTHORITY\SYSTEM, cmd=vmtoolsd.exe
    # pid=712, owner=NT AUTHORITY\SYSTEM, cmd=TrustedInstaller.exe
    # pid=1376, owner=WIN7-NOAV\avtest, cmd=wuauclt.exe
    # pid=1408, owner=WIN7-NOAV\avtest, cmd=wuauclt.exe
    # [19/12/13 11:09:53] Seppia: questa e' una vm che sta facendo aggiornamento, con i vmwaretools partiti (user logged on)

    user_logged = False
    vm_tools = False
    install = False
    try:
        processes = vm_manager.execute(vm, "list_processes");
    except:
        logging.exception("cannot get processes")
        #processes = vm_manager.execute(vm, "listProcesses");
        #logging.debug("listProcesses: %s" % processes)

    if not processes:
        try:
            sleep(60)
            logging.debug("trying listProcesses")
            procs = vm_manager.execute(vm, "listProcesses");
            logging.debug("listProcesses: %s" % procs)
            processes = helper.convert_processes(procs)
        except:
            logging.exception("listProcesses")

    if not processes:
        return "NOT-STARTED"

    try:
        logging.debug("%s, list_processes: %s" % (vm, [ (p["name"],p["owner"]) for p in processes] ))

        for process in processes:
            if process["owner"].endswith("avtest"):
                user_logged = True
                if process["name"] == "vmtoolsd.exe":
                    # owner=WIN7-NOAV\avtest, cmd=VMwareTray.exe
                    vm_tools = True
            if process["name"] == "wuauclt.exe" or process["name"] == "TrustedInstaller.exe":
                install = True
        # explorer, vmware solo se logged in
    except:
        logging.exception("error")

    if vm_tools:
        return "LOGGED-IN"
    if install:
        return "INSTALL"
    if not user_logged:
        return "LOGGED-OFF"
    else:
        return "NO-VM-TOOLS"

def execute(vm, protocol, args):
    """ server side """
    from AVMaster import vm_manager

    #logging.debug("    CS Execute")
    assert vm, "null vm"
    mq = protocol.mq


    check_avagent = (args == "AV_AGENT")

    mq.reset_connection(vm)
    ret = vm_manager.execute(vm, "startup")
    started = False
    if not ret:
        return False, "Not Started VM"

    max_install = 10
    max_tries = 10

    for i in range(3):
        sleep(10)
        if vm_manager.execute(vm, "is_powered_on"):
            for i in range(max_tries):
                if mq.check_connection(vm):
                    logging.debug("got connection from %s" % vm)
                    return True, "Started VM"

                for i in range(max_install):
                    status = get_status(vm)
                    logging.debug("%s, got status: %s" % (vm, status))

                    if status == "INSTALL":
                        logging.debug("waiting for the install to finish: %s/%s" % (i, max_install))
                        sleep(60)
                    else:
                        break

                if status == "LOGGED-IN":
                    logging.debug("%s, executing ipconfig, time: %s/%s" % (vm, i, max_tries))
                    started = vm_manager.execute(vm, "executeCmd", "c:\\windows\\system32\\ipconfig.exe") == 0
                    logging.debug("%s, executed ipconfig, ret: %s" % (vm, started))

                if started and not check_avagent:
                    return True, "Started VM"
                else:
                    sleep(20)

            if not started:
                logging.debug("%s: reboot requested" % vm)
                vm_manager.execute(vm, "reboot")
                sleep(60)
                continue

            return False, "Not started VM"
        else:
            logging.debug("%s: not yet powered" % vm)

    return False, "Error Occurred: Timeout while starting VM"


