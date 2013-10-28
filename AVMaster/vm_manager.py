import os
import sys

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

class VMManager(object):

    def __init__(self):
        pass

    def execute(self, vm_name, command, *args):
         if command in ["start", "stop"]:
             vm = VMachine(vm_conf_file, vm_name)
             attr = object.__getattribute__(vm, command)

         elif command in []:
             vmrun = VMRun()


    def __getattribute__(self, name):
        if name in ["start", "stop"]:
            print "vmmachine %s" % name

            return object.__getattribute__(self, name)
        if name in ["run"]:
            #vmman.executeCmd(vm, "%s\\%s" % (test_dir, buildbat), interactive=True, bg=True)
            return object.__getattribute__(self.vmman, name)

        else:
            # Default behaviour
            print "no test %s" % name
            return object.__getattribute__(self, name)



