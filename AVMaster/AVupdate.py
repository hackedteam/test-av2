import argparse
import sys
import os
from time import sleep

from lib.VMachine import VMachine
from lib.VMManager import VMManagerVS


if len(sys.argv) < 2:
	sys.stdout.write("[!] invalid syntax: \n%s <av name>\n" % sys.argv[0])
	sys.exit(0)

vm_conf_file = os.path.join("conf","vms.cfg")

# get configuration for AV update process (exe, vms, etc)

vm = VMachine(vm_conf_file, sys.argv[1])
vmman = VMManagerVS(conf_file)
#vmman = VMManagerVS(vmrun_path, vs_host, vs_user, vs_passwd)

# step 0: Switch Network oN

vmman.revertSnapshot(vm, vm.snapshot)
vmman.start(vm)

# executing script 1 and script 2


# sleep 3 hours
sleep(360*3)

vmman.reboot(vm)

vmman.refreshSnapshot(vm)

# step end: switch network oFF