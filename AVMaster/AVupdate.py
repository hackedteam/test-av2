import argparse
import sys
import os
import string
from time import sleep
from ConfigParser import ConfigParser

from lib.VMachine import VMachine
from lib.VMManager import VMManagerVS

'''
if len(sys.argv) < 2:
	sys.stdout.write("[!] invalid syntax: \n%s <av name>\n" % sys.argv[0])
	sys.exit(0)
'''

vm_conf_file = os.path.join("conf", "vms.cfg")
op_conf_file = os.path.join("conf", "operations.cfg")

# get configuration for AV update process (exe, vms, etc)

vmman = VMManagerVS(vm_conf_file)


# get vm names
c = ConfigParser()
c.read(op_conf_file)
vm_names = c.get("update", "machines")

# step 0: Switch Network oN


for vm_name in string.split(vm_names, ","):
	vm = VMachine(vm_conf_file, vm_name)
	
	vmman.revertSnapshot(vm, vm.snapshot)
	sleep(10)
	vmman.startup(vm)


	# executing scripts for vm and wait 3 hours
	vmman.executeCmd(vm, cmd)
	sleep(3600*3)
	vmman.reboot(vm)
	vmman.refreshSnapshot(vm)
'''

# then reverting and starting vm

vmman.revertSnapshot(vm, vm.snapshot)
vmman.start(vm)

sleep(60)


# executing script 1 and script 2

#vmman.executeCmd(vm, )

# sleep 3 hours

sleep(360*3)

vmman.reboot(vm)

vmman.refreshSnapshot(vm)

# step end: switch network oFF

'''