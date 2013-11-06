import os
import sys
import logging
import logging.config

from lib.core.VMRun import VMRun
from lib.core.VMachine import VMachine

from AVCommon import config

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

class VMManager:
    #def __init__(self, vm_conf_file = os.path.join("conf", "vms.cfg")):
    #    self.vm_conf_file = vm_conf_file

    vm_conf_file = "../AVMaster/conf/vms.cfg" #os.path.join("conf", "vms.cfg")

    @staticmethod
    def execute(vm_name, cmd, *args):
        vmachine_cmds = [
                    "startup", "shutdown", "reboot",
                    "get_snapshots", "revert_to_snapshot", "create_snapshot", "delete_snapshot",
                    "is_powered_on", "is_powered_off",
                    "make_directory", "get_file", "send_file" ]
        vmrun_cmds = [ "runTest", "takeScreenshot" ]

        logging.debug("command: %s" % cmd )

        try:
            vm = VMachine(vm_name)
            vm.get_params(VMManager.vm_conf_file)

            assert vm.config

            if cmd in vmrun_cmds:
                vmrun = VMRun(VMManager.vm_conf_file)
                f = getattr(vmrun, cmd)
                if not args: 
                    return f(vm)
                else: 
                    return f(vm, "".join(args))

            elif cmd in vmachine_cmds:
                f = getattr(vm, cmd)
                if not args: 
                    return f()
                else: 
                    return f(args)
            else:
                logging.error("command not found: %s" % cmd)
                raise Exception("Command not found")
        except AssertionError as ae:
            logging.error("Assertion found: %s" % ae)
            raise
        except Exception as e:
            logging.error("Exception found. %s" % e)
            raise
