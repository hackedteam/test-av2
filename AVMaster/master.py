import argparse
import sys
import os
import string
from time import sleep
from ConfigParser import ConfigParser
from multiprocessing import Pool

from lib.VMachine import VMachine
from lib.VMManager import VMManagerVS

def do_update(vm):
	return "updating %s" % vm

def do_dispatch(vm):
	return "dispatching tests for %s" % vm

def update(vm):
	try:
		vm = VMachine(vm_conf_file, vm_name)
		vmman.revertSnapshot(vm, vm.snapshot)
		sleep(10)
		vmman.startup(vm)
		# executing scripts for vm and wait 3 hours
		vmman.executeCmd(vm, cmd)
		sleep(3600*3)
		vmman.reboot(vm)
		vmman.refreshSnapshot(vm)

		return "%s updated"  % vm
	except:
		return "ERROR: %s is not updated"

def dispatch(vm):
	try:
		vm = VMachine(vm_conf_file, vm_name)
		vmman.revertSnapshot(vm, vm.snapshot)
		sleep(10)
		vmman.startup(vm)
		sleep(30)
		#	Copying files to guest
		# TODO: File list
		#vmman.copyFileToGuest()
		#
		#	Then execute
		vmman.executeCmd(vm, cmd)

		return "[*] %s test started" % vm

	except:
		return "Error: cannot dispatch tests for %s" % vm

def main():

	vm_conf_file = os.path.join("conf", "vms.cfg")
	op_conf_file = os.path.join("conf", "operations.cfg")

	# get configuration for AV update process (exe, vms, etc)

	vmman = VMManagerVS(vm_conf_file)

	#operation = sys.argv[1]
	operation = "dispatch"

	# get vm names
	c = ConfigParser()
	c.read(op_conf_file)
	vm_names = c.get("test", "machines").split(",")

	pool = Pool()
	if operation == "update": 
		print pool.map_async(do_update, ((vm) for vm in vm_names)).get()
	if operation == "dispatch": 
		print pool.map_async(do_dispatch, ((vm) for vm in vm_names)).get()
	#print pool.map_async(do_update, ((vm) for vm in vm_names)).get() if operation is "update"
	#print pool.map_async(do_dispatch, ((vm) for vm in vm_names)).get() if operation is "dispatch"
	#print r.get()

#if __name__ == "__main___":
main()