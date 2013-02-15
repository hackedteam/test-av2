import argparse
import sys
import os
import string
from time import sleep
from ConfigParser import ConfigParser
from multiprocessing import Pool

from lib.VMachine import VMachine
from lib.VMManager import VMManagerVS


def main():
	vm_conf_file = os.path.join("conf", "vms.cfg")
	op_conf_file = os.path.join("conf", "operations.cfg")

	# get configuration for AV update process (exe, vms, etc)

	vmman = VMManagerVS(vm_conf_file)


	# get vm names
	c = ConfigParser()
	c.read(op_conf_file)
	vm_names = c.get("update", "machines")


	po = Pool()

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


if __name__ == "__main___":
	main()