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
		self.config = ConfigParser()
		self.config.read(config_file)
		'''
		self.path   = self._getPath(config_file)
		self.host   = self._getHost(config_file)
		self.user   = self._getUser(config_file)
		self.passwd = self._getPasswd(config_file)
		'''
		self.path = self.config.get("vsphere", "path")
		self.host = self.config.get("vsphere", "host")
		self.path = self.config.get("vsphere", "user")
		self.host = self.config.get("vsphere", "passwd")

	def _getPath(self, conf_file):
		config = ConfigParser()
		config.read( conf_file )
		return config.get("vsphere", "path")


	def _getHost(self, conf_file):
		config = ConfigParser()
		config.read( conf_file )
		return config.get("vsphere", "host")

		
	def _getUser(self, conf_file):
		config = ConfigParser()
		config.read( conf_file )
		return config.get("vsphere", "user")

		
	def _getPasswd(self, conf_file):
		config = ConfigParser()
		config.read( conf_file )
		return config.get("vsphere", "passwd")

	def _run_cmd(vmx, cmd, args=[], vmx_creds=[]):
		pargs = [   path,
					"-T", "vc",
					"-h", self.host,
					"-u", self.user, "-p", self.passwd, cmd, vmx.path ]
		if vm_cred != [] and len(vm_cred) == 2:
			idx = pargs.index("-p")+2
			
		pargs.extend(args)
		subprocess.call(pargs)

	'''
	def startup(self, vmx):
		sys.stdout.write("[*] Starting %s!\r\n" % vmx)
		self._run_cmd(vmx, "start")

	def shutdown(self, vmx):
		sys.stdout.write("[*] Stopping %s!\r\n" % vmx)
		self._run_cmd(vmx, "stop")

	def reboot(self, vmx):
		sys.stdout.write("[*] Rebooting %s!\r\n" % vmx)
		self._run_cmd(vmx, "reset", ["soft"])

	def suspend(self, vmx):
		sys.stdout.write("[*] Rebooting %s!\r\n" % vmx)
		self._run_cmd(vmx, "suspend", ["soft"])

	def copyFileToGuest(self, vmx, file_path = []):
		sys.stdout.write("[*] Copying file %s to %s on %s).\n" % (src_file, dst_file,  vmx))
		self._run_cmd(vmx, "CopyFileFromHostToGuest", file_path)

	def copyFileFromGuest(self, vmx, file_path = []):
		sys.stdout.write("[*] Copying file %s to %s from %s).\n" % (src_file, dst_file,  vmx))
		self._run_cmd(vmx, "CopyFileFromHostFromGuest", file_path)

	def createSnapshot(self, vmx, snapshot):
		sys.stdout.write("[*] Creating snapshot %sfor %s.\n" % (vmx.snapshot,vmx))
		self._run_cmd(vmx, "snapshot", [snapshot])

	def deleteSnapshot(self, vmx, snapshot):
		sys.stdout.write("[*] Deleting snapshot %sfor %s.\n" % (vmx.snapshot,vmx))
		self._run_cmd(vmx, "deleteSnapshot", [snapshot])

	def revertSnapshot(self, vmx, snapshot):
		sys.stdout.write("[*] Reverting snapshot %sfor %s.\n" % (vmx.snapshot,vmx))
		self._run_cmd(vmx, "revertToSnapshot", [snapshot])

	def refreshSnapshot(self, vmx):
		sys.stdout.write("[*] Refreshing snapshot %sfor %s.\n" % (vmx.snapshot,vmx))
		self.deleteSnapshot(vmx, vmx.snapshot)
		self.createSnapshot(vmx, vmx.snapshot)

	'''

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
		sys.stdout.write("[*] Creating snapshot %sfor %s.\n" % (vmx.snapshot,vmx))
		subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"snapshot", vmx.path, snapshot])
	
	def deleteSnapshot(self, vmx, snapshot):
		sys.stdout.write("[*] Deleting snapshot %sfor %s.\n" % (vmx.snapshot,vmx))
		subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"deleteSnapshot", vmx.path, snapshot])
						
	def refreshSnapshot(self, vmx, snapshot):
		sys.stdout.write("[*] Refreshing snapshot %sfor %s.\n" % (vmx.snapshot,vmx))
		self.deleteSnapshot(vmx, snapshot)
		self.createSnapshot(vmx, snapshot)
						
	def revertSnapshot(self, vmx, snapshot):
		sys.stdout.write("[*] Reverting snapshot %sfor %s.\n" % (vmx.snapshot,vmx))
		subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"revertToSnapshot", vmx.path, snapshot])

	def mkdirInGuest(self, vmx, dir_path):
		sys.stdout.write("[*] Creating directory %s into %s.\n" % (dir_path,vmx))
		subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"-gu", "%s" % vmx.user, "-gp", "%s" % vmx.passwd,
						"CreateDirectoryInGuest", vmx.path, dir_path])

	def copyFileToGuest(self, vmx, src_file, dst_file):
		sys.stdout.write("[*] Copying file %s to %s on %s).\n" % (src_file, dst_file,  vmx))
		subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"-gu", "%s" % vmx.user, "-gp", "%s" % vmx.passwd,
						"CopyFileFromHostToGuest", vmx.path, src_file, dst_file])

	def copyFileFromGuest(self, vmx, src_file, dst_file):
		sys.stdout.write("[*] Copying file %s to %s from %s).\n" % (src_file, dst_file,  vmx))
		subprocess.call([self.path,
						"-T", "vc",
						"-h", self.host,
						"-u", self.user, "-p", self.passwd,
						"-gu", "%s" % vmx.user, "-gp", "%s" % vmx.passwd,
						"CopyFileFromGuestToHost", vmx.path, src_file, dst_file])

	def executeCmd(self, vmx, cmd, script=None):
		sys.stdout.write("[*] Executing %s %s in %s.\r\n" % (cmd, script, vmx))
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
		sys.stdout.write("[*] Taking screenshot from %s.\n" % vmx)
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
		sys.stdout.write("[*] Creating new snapshot %s for %s.\n" % (vmx.snapshot,vmx))
		subprocess.call([self.path,
						"-T", "fusion",
						"snapshot", vmx.path, vmx.snapshot])
						
	def revertSnapshot(self, vmx):
		sys.stdout.write("[*] Reverting %s to snapshot %s.\n" % (vmx, vmx.snapshot))
		subprocess.call([self.path,
						"-T", "fusion",
						"revertToSnapshot", vmx.path, vmx.snapshot])

	def copyFileToGuest(self, vmx, src_file, dst_file):
		sys.stdout.write("[*] Copying file %s to %s on %s.\n" % (src_file, dst_file, vmx))
		subprocess.call([self.path,
						"-T", "fusion",
						"CopyFileFromHostToGuest", vmx.path, src_file, dst_file])

	def executeCmd(self, vmx, cmd, script=None):
		if script is not None:
			sys.stdout.write("[*] Executing %s %s in %s.\r\n" % (cmd, script, vmx))
			proc = subprocess.call([self.path,
						"-T", "fusion",
						"-gu", vmx.user, "-gp", vmx.passwd,
						"runProgramInGuest", vmx.path, cmd, script])			
		else:
			sys.stdout.write("[*] Executing %s in %s.\r\n" % cmd, vmx)
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