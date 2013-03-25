import subprocess
import sys
import os

from time import sleep
from datetime import datetime
from ConfigParser import ConfigParser

from pysphere import VIServer

class vSphere:
	hostname = ""
	username = ""
	password = ""

	def __init__(self, vm_path):
		self.vm_path = vm_path

	def __enter__(self):
		self.server   = VIServer()
		self.server.connect(self.hostname, self.username, self.password)
		print "DBG connect"
		vm  = self.server.get_vm_by_path(self.vm_path)
		return vm

	def __exit__(self, type, value, traceback):
		try:
			self.server.disconnect()
			print "DBG disconnect"
		except VIException as e:
			print "DBG problem in disconnection. Fault is: %s" % e.fault
			pass


class VMRun:
	def __init__(self, config_file):
		self.config = ConfigParser()
		self.config.read(config_file)

		self.path 	= self.config.get("vsphere", "path")
		self.host 	= self.config.get("vsphere", "host")
		self.user   = self.config.get("vsphere", "user")
		self.passwd = self.config.get("vsphere", "passwd")

	def _run_cmd(self, vmx, cmd, args=[], vmx_creds=[], popen=False, timeout=40):
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
			return self._run_popen(pargs, timeout)
		else:
			return self._run_call(pargs)

	def _run_call(self, pargs):
		return subprocess.call(pargs)

	def _run_popen(self, pargs, timeout=40):
		p = subprocess.Popen(pargs, stdout=subprocess.PIPE)

		executed = False
		tick = 0

		while executed is False:
			sleep(20)
			tick += 1
			if p.poll() != None: #process is executed and ret.poll() has the return code
				executed = True
			if tick >= timeout * 3: 
				print "DBG run_popen timeout"
				return []

		if p.poll() == 0:
			return p.communicate()[0]
		else:
			print "DBG p.poll is 0"
			return []


	def startup(self, vmx):
		sys.stdout.write("[%s] Starting!\r\n" % vmx)
		self._run_cmd(vmx, "start")

	def shutdown(self, vmx):
		sys.stdout.write("[%s] Stopping!\r\n" % vmx)
		self._run_cmd(vmx, "stop")

	def shutdownUpgrade(self, vmx):
		r = self.executeCmd(vmx, "c:\\WINDOWS\\system32\\shutdown.exe", ["/s"], timeout=105) #["/s","/t","0"])
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
		untouchables = [ "ready", "activated", "_datarecovery_" ] 

		sys.stdout.write("[%s] Refreshing snapshot.\n" % vmx)

		# create new snapshot
		date = datetime.now().strftime('%Y%m%d-%H%M')
		self.createSnapshot(vmx, "%s" % date)
		if delete == True:
			snaps = self.listSnapshots(vmx)
			print "DBG snapshots %s" % snaps
 			if len(snaps) > 0 and snaps[-2] not in untouchables and "manual" not in snaps[-2]:
 				print "DBG deleting %s" % snaps[-2]
				self.deleteSnapshot(vmx, snaps[-2])

	def revertLastSnapshot(self,vmx):
		snap = self.listSnapshots(vmx)
		if len(snap) > 0:
			
			for s in range(len(snap)-1,-1,-1):
				snapshot = snap[s]
				if snapshot != "_datarecovery_":
					self.revertSnapshot(vmx, snap[s])
					return "[%s] Reverted with snapshot %s" % (vmx, snap[s])
				else:
					print "DBG snapshot _datarecovery_ found!"
			return "[%s] ERROR: no more snapshot to try" % vmx
		else:
			return "[%s] ERROR: no snapshots!" % vmx

	def mkdirInGuest(self, vmx, dir_path):
		sys.stdout.write("[%s] Creating directory %s.\n" % (vmx,dir_path))
		self._run_cmd(vmx, "CreateDirectoryInGuest", [dir_path], [vmx.user,vmx.passwd])

	def listDirectoryInGuest(self, vmx, dir_path):
		sys.stdout.write("[%s] Listing directory %s.\n" % (vmx,dir_path))
		return self._run_cmd(vmx, "listDirectoryInGuest", [dir_path], [vmx.user,vmx.passwd], popen=True)

	def deleteDirectoryInGuest(self, vmx, dir_path):
		sys.stdout.write("[%s] Delete directory %s.\n" % (vmx,dir_path))
		self._run_cmd(vmx, "DeleteDirectoryInGuest", [dir_path], [vmx.user,vmx.passwd])

	def copyFileToGuest(self, vmx, src_file, dst_file):
		sys.stdout.write("[%s] Copying file from %s to %s.\n" % (vmx, src_file, dst_file))
		self._run_cmd(vmx, "CopyFileFromHostToGuest", [src_file, dst_file], [vmx.user, vmx.passwd])

	def copyFileFromGuest(self, vmx, src_file, dst_file):
		sys.stdout.write("[%s] Copying file from %s to %s.\n" % (vmx, src_file, dst_file))
		self._run_cmd(vmx, "CopyFileFromGuestToHost", [src_file, dst_file], [vmx.user, vmx.passwd])

	def executeCmd(self, vmx, cmd, args=[], timeout=40, interactive=False): 
		sys.stdout.write("[%s] Executing %s\n" % (vmx,cmd))
		cmds = []
		if interactive is True:
			cmds.append("-interactive")
		cmds.append(cmd)
		cmds.extend(args)
		return self._run_cmd(vmx, 
							 "runProgramInGuest", 
							 cmds, 
							 [vmx.user, vmx.passwd], 
							 popen=True, timeout=timeout)

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
