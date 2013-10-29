import os
import sys

from lib.core.VMRun import VMRun
from lib.core.VMachine import VMachine

vm_conf_file = os.path.join("conf", "vms.cfg")

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

class VMManager:
    def __init__(self):
        pass

    def execute(self, vm_name, cmd, *args):
        vmachine_cmds = [ 
                    "startup", "shutdown", "reboot", 
                    "get_snapshots", "revert_to_snapshot", "create_snapshot", "delete_snapshot",
                    "is_powered_on", "is_powered_off",
                    "make_directory", "get_file", "send_file" ]
        vmrun_cmds = [ "executeCmd", "runTest", "takeScreenshot" ]

        vm = VMachine(vm_conf_file, vm_name)

        if cmd in vmrun_cmds:
            vmrun = VMRun(vm_conf_file)
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
            print "COMMAND NOT FOUND"

def test():
    from time import sleep

    vmm = VMManager()
    print "TEST CMD WITHOUT ARGS:"
    vmm.execute("avg","startup")

    while vmm.execute("avg", "is_powered_on") is False:
        print "sleeping 5 secs"
        sleep(5)

    sleep(180)
    print "TEST CMD WITH ARGS:"
    vmm.execute("avg", "runTest", 
        "C:\\Users\AVTEST\Desktop\\AVTEST\\build_exploit_web_minotauro.bat")
    vmm.execute("avg", "takeScreenshot", "/tmp/gie.png")
    vmm.execute("avg","shutdown")

    while vmm.execute("avg", "is_powered_off") is False:
        print "still shutting down"
        sleep(5)

    print "TESTING NOT CMD"
    vmm.execute("avg","killah")

    print "end"

if __name__ == "__main__":
    test()
