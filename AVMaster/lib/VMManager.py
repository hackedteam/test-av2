import subprocess
import sys
import os

from time import sleep
from datetime import datetime
from ConfigParser import ConfigParser


class VMManagerVS:
	def __init__(self, config_file):
		self.config = ConfigParser()
		self.config.read(config_file)

		self.path = self.config.get("vsphere", "path")
		self.host = self.config.get("vsphere", "host")
		self.user = self.config.get("vsphere", "user")
		self.passwd = self.config.get("vsphere", "passwd")


	def _run_cmd(self, vmx, cmd, args=[], vmx_creds=[], popen=False, timeout=30):
		pargs = [   self.path,
					"-T", "vc",
					"-h", self.host,
					"-u", self.user, "-p", self.passwd, cmd, vmx.path ]
		if vmx_creds != [] and len(vmx_creds) == 2:
			idx = pargs.index("-p")+2
			cred = "-gu %s -gp %s" % ( vmx_creds[0], vmx_creds[1] )
			pargs = pargs[0:idx] + cred.split() + pargs[idx:]
			
		pargs.extend(args)
		if popen == True:
			return self._run_popen(pargs)
		else:
			return self._run_call(pargs)

	def _run_call(self, pargs):
		return subprocess.call(pargs)

	def _run_popen(self, pargs):
		p = subprocess.Popen(pargs, stdout=subprocess.PIPE)

		executed = False
		tick = 0

		while executed is False:
			sleep(20)
			tick += 1
			if p.poll() != None: #process is executed and ret.poll() has the return code
				executed = True
			if tick >= 45 * 3: ## 3 (ticks in 1 min) * 35 (minutes) = 105 min
				return False

		if p.poll() == 0:
			return p.communicate()[0]
		else:
			return False


	def startup(self, vmx):
		sys.stdout.write("[%s] Starting!\r\n" % vmx)
		self._run_cmd(vmx, "start")

	def shutdown(self, vmx):
		sys.stdout.write("[%s] Stopping!\r\n" % vmx)
		self._run_cmd(vmx, "stop")

	def shutdownUpgrade(self, vmx):
		r = self.executeCmd(vmx, "c:\\WINDOWS\\system32\\shutdown.exe", ["/s"]) #["/s","/t","0"])
		if r is False:
			return False
		return True

	def reboot(self, vmx):
		sys.stdout.write("[%s] Rebooting!\r\n" % vmx)
		self._run_cmd(vmx, "reset", ["hard"])

	def suspend(self, vmx):
		sys.stdout.write("[%s] Suspending!\r\n" % vmx)
		self._run_cmd(vmx, "suspend", ["soft"])

	def createSnapshot(self, vmx, snapshot):
		sys.stdout.write("[%s] Creating snapshot %s.\n" % (vmx, snapshot))
		self._run_cmd(vmx, "snapshot", [snapshot])

	def deleteSnapshot(self, vmx, snapshot):
		sys.stdout.write("[%s] Deleting snapshot %s.\n" % (vmx, snapshot))
		self._run_cmd(vmx, "deleteSnapshot", [snapshot])

	def revertSnapshot(self, vmx, snapshot):
		sys.stdout.write("[%s] Reverting snapshot %s.\n" % (vmx, snapshot))
		self._run_cmd(vmx, "revertToSnapshot", [snapshot])

	def refreshSnapshot(self, vmx, delete=True):
		sys.stdout.write("[%s] Refreshing snapshot.\n" % vmx)

		# create new snapshot
		date = datetime.now().strftime('%Y%m%d-%H%M')
		self.createSnapshot(vmx, "%s" % date)
		if delete == True:
			snaps = self.listSnapshots(vmx)
			if len(snaps) > 0 and snaps[-2] != "ready":
				self.deleteSnapshot(vmx, snaps[-2])



	def revertLastSnapshot(self,vmx):
		snap = self.listSnapshots(vmx)
		if len(snap) > 0:
			self.revertSnapshot(vmx, snap[-1])
		else:
			return "[%s] ERROR: no snapshots!" % vmx

	def mkdirInGuest(self, vmx, dir_path):
		sys.stdout.write("[%s] Creating directory %s.\n" % (vmx,dir_path))
		self._run_cmd(vmx, "CreateDirectoryInGuest", [dir_path], [vmx.user,vmx.passwd])

	def copyFileToGuest(self, vmx, src_file, dst_file):
		sys.stdout.write("[%s] Copying file from %s to %s.\n" % (vmx, src_file, dst_file))
		self._run_cmd(vmx, "CopyFileFromHostToGuest", [src_file, dst_file], [vmx.user, vmx.passwd])

	def copyFileFromGuest(self, vmx, src_file, dst_file):
		sys.stdout.write("[%s] Copying file from %s to %s.\n" % (vmx, src_file, dst_file))
		self._run_cmd(vmx, "CopyFileFromGuestToHost", [src_file, dst_file], [vmx.user, vmx.passwd])

	def executeCmd(self, vmx, cmd, args=[]): 
		sys.stdout.write("[%s] Executing %s\n" % (vmx,cmd))
		cmds = []
		cmds.append(cmd)
		cmds.extend(args)
		return self._run_cmd(vmx, "runProgramInGuest", cmds, [vmx.user, vmx.passwd], popen=True)


	def listProcesses(self, vmx):
		sys.stdout.write("[%s] List processes\n" % vmx)
		out = self._run_cmd(vmx, "listProcessesInGuest", vmx_creds=[vmx.user,vmx.passwd], popen=True)
		return out

	def takeScreenshot(self, vmx, out_img):
		sys.stdout.write("[%s] Taking screenshot.\n" % vmx)
		self._run_cmd(vmx, "captureScreen", [out_img], [vmx.user, vmx.passwd])

	def VMisRunning(self, vmx):
		res = self._run_cmd(vmx, "list", popen=True)
		if vmx.path[1:-1] in res:
			return True
		return False

	def listSnapshots(self, vmx):
		out = self._run_cmd(vmx, "listSnapshots", popen=True).split("\n")
		return out[1:-1]

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
