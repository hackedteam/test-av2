import subprocess
import sys
import os

from ConfigParser import ConfigParser

class VMManagerVS:
	#def __init__(self, path, host=None, user=None, passwd=None):
	def __init__(self, config_file):
		'''
		self.path = path
		self.host = host
		self.user = user
		self.passwd = passwd
		'''
		self.path   = self._getPath(config_file)
		self.host   = self._getHost(config_file)
		self.user   = self._getUser(config_file)
		self.passwd = self._getPasswd(config_file)


	def _getPath(conf_file):
		config = ConfigParser()
		config.read( conf_file )
		return config.get("vsphere", "path")


	def _getHost(config_file):
		config = ConfigParser()
		config.read( conf_file )
		return config.get("vsphere", "host")

		
	def _getUser(config_file):
		config = ConfigParser()
		config.read( conf_file )
		return config.get("vsphere", "user")

		
	def _getPasswd(config_file):
		config = ConfigParser()
		config.read( conf_file )
		return config.get("vsphere", "passwd")

		
	def startup(self, vmx):
		sys.stdout.write("[*] Startup %s!\r\n" % vmx)
		subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"start", vmx.path])
	
	def shutdown(self, vmx):
		sys.stdout.write("[*] Shutdown %s!\r\n" % vmx)
		subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"stop", vmx.path])

	def reboot(self, vmx):
		sys.stdout.write("[*] Rebooting %s!\r\n" % vmx)
		subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"reset", vmx.path, "soft"])

	def suspend(self, vmx):
		sys.stdout.write("[*] Suspending %s!\r\n" % vmx)
		subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"suspend", vmx.path, "soft"])

	def createSnapshot(self, vmx, snapshot):
		sys.stdout.write("[*] Creating new current snapshot.\n")
		subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"snapshot", vmx.path, snapshot])
	
	def deleteSnapshot(self, vmx, snapshot):
		sys.stdout.write("[*] Deleting current snapshot.\n")
		subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"deleteSnapshot", vmx, snapshot])
						
	def refreshSnapshot(self, vmx, snapshot):
		self.deleteSnapshot(vmx, snapshot)
		self.createSnapshot(vmx, snapshot)
						
	def revertSnapshot(self, vmx, snapshot):
		sys.stdout.write("[*] Reverting to current snapshot.\n")
		subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"revertToSnapshot", vmx.path, snapshot])

	def copyFileToGuest(self, vmx, src_file, dst_file):
		sys.stdout.write("[*] Copying file %s into guest (on dir %s).\n" % (src_file, dst_file))
		subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"CopyFileFromHostToGuest", vmx.path, src_file, dst_file])

	def executeCmd(self, vmx, cmd, script=None):
		sys.stdout.write("[*] Executing %s %s.\r\n" % (cmd, script))
		if script is not None:
			subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"-gu", "%s" % vmx.user, "-gp", "%s" % vmx.passwd,
						"runProgramInGuest", vmx.path, cmd, script])			
		else:
			subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"-gu", "%s" % vmx.user, "-gp", "%s" % vmx.passwd,
						"runProgramInGuest", vmx.path, cmd])
						
	def takeScreenshot(self, vmx, out_img):
		sys.stdout.write("[*] Taking screenshot of %s.\n" % vmx)
		subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"-gu","%s" %  vmx.user, "-gp", "%s" % vmx.passwd,
						"captureScreen", vmx.path, out_img])						

class VMManagerFus:
	def __init__(self, path):
		self.path = path

	def startup(self, vmx):
		sys.stdout.write("[*] Startup %s!\r\n" % vmx)
		subprocess.call([self.path,
						"-T", "fusion",
						"start", vmx.path])
	
	def shutdown(self, vmx):
		sys.stdout.write("[*] Shutdown %s!\r\n" % vmx)
		subprocess.call([self.path,
						"-T", "fusion",
						"stop", vmx.path])

	def reboot(self, vmx):
		sys.stdout.write("[*] Rebooting %s!\r\n" % vmx)
		subprocess.call([self.path,
						"-T", "fusion",
						"reset", vmx.path, "soft"])

	def suspend(self, vmx):
		sys.stdout.write("[*] Suspending %s!\r\n" % vmx)
		subprocess.call([self.path,
						"-T", "fusion",
						"suspend", vmx.path, "soft"])

	def refreshSnapshot(self, vmx):
		sys.stdout.write("[*] Deleting current snapshot.\n")
		subprocess.call([self.path,
						"-T", "fusion",
						"deleteSnapshot", vmx.path, vmx.snapshot])
		sys.stdout.write("[*] Creating new current snapshot.\n")
		subprocess.call([self.path,
						"-T", "fusion",
						"snapshot", vmx.path, vmx.snapshot])
						
	def revertSnapshot(self, vmx):
		sys.stdout.write("[*] Reverting to current snapshot.\n")
		subprocess.call([self.path,
						"-T", "fusion",
						"revertToSnapshot", vmx.path, vmx.snapshot])

	def copyFileToGuest(self, vmx, src_file, dst_file):
		sys.stdout.write("[*] Copying file %s into guest (on dir %s).\n" % (src_file, dst_file))
		subprocess.call([self.path,
						"-T", "fusion",
						"CopyFileFromHostToGuest", vmx.path, src_file, dst_file])

	def executeCmd(self, vmx, cmd, script=None):
		if script is not None:
			sys.stdout.write("[*] Executing %s %s.\r\n" % (cmd, script))
			proc = subprocess.call([self.path,
						"-T", "fusion",
						"-gu", vmx.user, "-gp", vmx.passwd,
						"runProgramInGuest", vmx.path, cmd, script])			
		else:
			sys.stdout.write("[*] Executing %s.\r\n" % cmd)
			proc = subprocess.call([self.path,
						"-T", "fusion",
						"-gu", vmx.user, "-gp", vmx.passwd,
						"runProgramInGuest", vmx.path, cmd])
		if proc != 0:
			return False	
		return True			


	def takeScreenshot(self, vmx, out_img):
		sys.stdout.write("[*] Taking screenshot of %s.\n" % vmx)
		subprocess.call([self.path,
						"-T", "fusion",
						"-gu", vmx.user, "-gp", vmx.passwd,
						"captureScreen", vmx.path, out_img])