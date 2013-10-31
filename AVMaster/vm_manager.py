import os
import sys
import logging
import logging.config

from lib.core.VMRun import VMRun
from lib.core.VMachine import VMachine


prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

class VMManager:
    def __init__(self, vm_conf_file = os.path.join("conf", "vms.cfg")):
        self.vm_conf_file = vm_conf_file

    def execute(self, vm_name, cmd, *args):
        vmachine_cmds = [
                    "startup", "shutdown", "reboot",
                    "get_snapshots", "revert_to_snapshot", "create_snapshot", "delete_snapshot",
                    "is_powered_on", "is_powered_off",
                    "make_directory", "get_file", "send_file" ]
        vmrun_cmds = [ "runTest", "takeScreenshot" ]

        logging.debug("command: %s" % cmd )

        try:
            vm = VMachine(vm_name)
            vm.get_params(self.vm_conf_file)

            assert vm.config

            if cmd in vmrun_cmds:
                vmrun = VMRun(self.vm_conf_file)
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
                logging.debug("command %s not found." % cmd)
                return False
        except AssertionError as ae:
            logging.info("Assertion found: %s" % ae)
            return False
        except Exception as e:
            logging.info("Exception found. %s" % e)
            return False

"""
def test():
    from time import sleep

    vmm = VMManager()
    logging.debug( "TEST CMD WITHOUT ARGS:")
    vmm.execute("avg","startup")
    vmm.execute("avast","startup")

    while vmm.execute("avg", "is_powered_on") is False:
        logging.debug( "sleeping 5 secs waiting for avg")
        sleep(5)

    while vmm.execute("avast", "is_powered_on") is False:
        logging.debug( "sleeping 5 secs waiting for avast")
        sleep(5)

    sleep(180)
    for vm in ["avg", "avast"]:
        logging.debug( "TEST CMD WITH ARGS:")
        vmm.execute(vm, "runTest", "C:\\Users\AVTEST\Desktop\\AVTEST\\build_exploit_web_minotauro.bat")
        vmm.execute(vm, "takeScreenshot", "/tmp/gie.png")
        vmm.execute(vm,"shutdown")

        while vmm.execute(vm, "is_powered_off") is False:
            logging.debug("still shutting down %s" % vm )
            sleep(5)

        logging.debug( "TESTING NOT CMD")
        vmm.execute("avg","killah")

        logging.debug("end %s" % vm)

if __name__ == "__main__":
    logging.config.fileConfig('../../logging.conf')
    logging.info("test")
    test()
"""