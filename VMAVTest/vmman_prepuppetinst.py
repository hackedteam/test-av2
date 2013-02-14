import sys
from time import sleep

from VMManager import VMManagerFus
from VMMachine import VMMachine
from ConsoleAPI import API

conf_file = "vms.cfg"
vmrun_path = "/Applications/VMwareFusion.app/Contents/Library/vmrun"

# hostname change script paths
host_script_src = ""
host_script_dst = ""

# ip addr of ext if script paths
addr_script_src = ""
addr_script_dst = ""

# puppet installer path
puppet_path = "C:\\Users\\avtest\\Desktop\\puppet-3.1.0-rc1.msi"

# vSphere creds
host=""
user=""
passwd=""

#
#	Defining VM Manager
#
vmman = VMManagerVS(vmrun_path, host, user, passwd))

#
#	Defining all vms you need
#
avg = VMMachine(conf_file, "avg")

# 1. startup vm
vmman.startup(avg)
#
# 2. copy files
vmman.copyFileToGuest(avg, addr_script_src, addr_script_dst)
vmman.copyFileToGuest(avg, host_script_src, host_script_dst)
#
# 3. run scripts
x = vmman.executeCmd(avg, host_script_dst)
if x is not True:
	sys.stdout.write("[!] error executing %s\n" % host_script_dst)
	#vmman.shutdown(avg)
	#sys.exit(0)

x = vmman.executeCmd(avg, addr_script_dst)
if x is not True:
	sys.stdout.write("[!] error executing %s\n" % addr_script_dst)
	#vmman.shutdown(avg)
	#sys.exit(0)

#
# 4. wait for reboot
vmman.reboot(avg)

#
# 5. run puppet installer (maybe issues with UAC)
x = vmman.executeCmd(avg, puppet_path)
if x is not True:
	sys.stdout.write("[!] error executing %s\n" % addr_script_dst)
	#vmman.shutdown(avg)
	#sys.exit(0)
