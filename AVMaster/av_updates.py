import argparse
import sys
from time import sleep

from lib.config import Config
from lib.command import Command			

class AVUpdate:
	def __init__(self):
		""" Configure command interface through Config class
		"""
		self.config_file = "c:/test-av/conf/vmware.conf"
		self.conf = Config(self.config_file)
		#
		# you can redefine the Command class providing vmrun full path:
		# self.cmd = Command("vmrun full path")
		#
		# TODO:
		#	- Command class with one argument
		self.cmd = Command(self.conf.path, self.conf.host, self.conf.user, self.conf.passwd)
		
		# full paths of script neede for update
		self.netENScript="c:/Users/avtest/Desktop/EnableIF.bat"
		self.netDISScript="c:/Users/avtest/Desktop/DisableIF.bat"
		self.updScript="C:/Users/avtest/Desktop/AVUpdate.bat"

	def doUpdate(self, vmx):
		if vmx == 'all':
			#update all vms
			vms = self.conf.getMachines()
			
			sys.stdout.write("[*] Starting all guests.\n")
			for vm in vms:
				self.cmd.startup(self.conf.getVmx(vm))
				sleep(5)
				
			sys.stdout.write("[*] Enabling Networking on guests.\n")
			for vm in vms:
				self.cmd.executeCmd(self.conf.getVmx(vm), self.netENScript)

			sys.stdout.write("[*] Updating Antiviruses on guests.\n")
			for vm in vms:
				self.cmd.executeCmd(self.conf.getVmx(vm), self.updScript)
			sleep(60*len(vms))
			sys.stdout.write("[*] Done.\n")
					
		else:
			sys.stdout.write("[*] Starting %s.\n" % vmx)
			self.cmd.startup(self.conf.getVmx(vmx))
			sleep(60)
			sys.stdout.write("[*] Enabling Networking on %s.\n" % vmx)
			self.cmd.executeCmd(self.conf.getVmx(vmx), self.netENScript)
			sleep(10)
			sys.stdout.write("[*] Updating Antivirus on %s.\n" % vmx)
			self.cmd.executeCmd(self.conf.getVmx(vmx), self.updScript)
			sleep(60*5)
			sys.stdout.write("[*] Done.\n")
			
	
	def doReboot(self, vmx):
		if vmx == "all":
			vms = self.conf.getMachines()
			sys.stdout.write("[*] Disabling network on guests.\n")
			for vm in vms:
				self.cmd.executeCmd(self.conf.getVmx(vm), self.netDISScript)
				sleep(15)
			sys.stdout.write("[*] Rebooting guests.\n")
			for vm in vms:
				self.cmd.reboot(self.conf.getVmx(vm))
				sleep(5)	
		else:
			vm = self.conf.getVmx(vmx)
			sys.stdout.write("[*] Disabling network on %s.\n" % vmx)
			self.cmd.executeCmd(vm, self.netDISScript)
			sys.stdout.write("[*] Rebooting %s.\n" % vmx)
			self.cmd.reboot(vm)


	def refreshShot(self, vmx):
		if vmx == "all":
			sys.stdout.write("[*] Refresh snapshots on guests.\n")
			for vm in vms:
				self.cmd.refreshSnapshot(self.conf.getVmx(vm), 'current')
				sleep(30)
				self.cmd.suspend(self.conf.getVmx(vm))

		else:
			sys.stdout.write("[*] Refresh snapshot of %s" % vmx)
			self.cmd.refreshSnapshot(self.conf.getVmx(vmx), 'current')
			self.cmd.suspend(self.conf.getVmx(vmx))
			

'''
sys.stdout.write("Lets start!\n\n")
wu = WinUpdate()
wu.doUpdate('norman')
wu.doReboot('norman')
wu.refreshShot('norman')
'''
if len(sys.argv) < 1:
	sys.exit(0)

sys.stdout.write("Lets start!\n\n")
wu = AVUpdate()
wu.doUpdate(sys.argv[1])
wu.doReboot(sys.argv[1])
wu.refreshShot(sys.argv[1])
sys.stdout.write("Everything is done!\n\n")