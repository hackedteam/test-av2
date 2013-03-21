import os

from time import sleep
from ConfigParser import ConfigParser, NoSectionError
from pysphere.resources.vi_exception import VIException

class connection:
	def __init__(self, vi_srv):
		self.srv = vi_srv

	def __enter__(self):
		self.srv.connect()

	def __exit__(self, type, value, traceback):
		try:
			self.srv.disconnect()
		except VIException as e:
			print "DBG problem in disconnection. Fault is: %s" % e.fault
			pass

class VMachine:
	def __init__(self, conf_file, vi_srv, name):
		self.name = name
		try:
			self.config = ConfigParser()
			self.config.read( conf_file )
			self.path     = self.config.get("vms", name)
			self.snapshot = self.config.get("vm_config", "snapshot")
			self.user     = self.config.get("vm_config", "user")
			self.passwd   = self.config.get("vm_config", "passwd")
			self.vi_srv   = vi_srv
			self.vm 	  = self.vi_srv.get_vm(self.path)
		except NoSectionError:
			print "[!] VM or VM stuff not found on %s" % conf_file
			return None
		
	def __str__(self):
		return "%s" % self.name

	#	FUNCTIONS

	def refresh_snapshot(self, delete=True):
		untouchables = [ "ready", "activated", "_datarecovery_" ]
		date = datetime.now().strftime('%Y%m%d-%H%M')
		self.create_snapshot(date)
		if delete is True:
			snap_list = self.list_snapshots()
			for snap in snap_list:
				print snap.get_name()
			if len(snap_list) > 0 and snap_list[-2].get_name() not in untouchables and "manual" not in snap_list[-2].get_name():
				print "DBG deleting %s" % snap_list[-2].get_name()
				self.delete_snapshot(snap_list[-2].get_name())


	def get_all_pid(self):
		pids = []
		procs = self.list_processes()

		if procs is None:
			return None

		for proc in procs:
			pids.append(proc['pid'])

		return pids

	def execute_cmd(self, cmd, args=[], timeout=40):
		pid = self.start_process(cmd, args)
		print "DBG created process %s with pid %s" % (cmd, pid)

		tick = 0

		while pid in self.get_all_pid():
			if tick >= timeout * 6:
				break
			tick += 1
			sleep(10)

		print self.get_all_pid()
		print "exiting"

	def shutdown_upgrade(self, timeout=120):
		
		tick = 0

		shutdown_cmd = "C:\\WINDOWS\\system32\\shutdown.exe"
		args = [ "/s", "/t", "0" ]
		
		self.execute_cmd(shutdown_cmd, args=args)

		while self.is_powered_off() is False:
			if tick >= timeout * 60:
				tick += 1
				sleep(15)
				return False
		return True

	#	TASKS

	def startup(self):
		return self._run_task("power_on")

	def shutdown(self):
		return self._run_task("power_off")

	def suspend(self):
		return self._run_task("suspend")

	def get_snapshots(self):
		return self._run_task("get_snapshots")

	def revert_last_snapshot(self):
		return self._run_task("revert_to_snapshot")

	def create_snapshot(self, name):
		return self._run_task("create_snapshot", name)

	def delete_snapshot(self, name):
		return self._run_task("delete_named_snapshot", name)

	# 	COMMANDS

	def is_powered_off(self):
		return self._run_cmd("is_powered_off")

	def login_in_guest(self):
		return self._run_cmd("login_in_guest", self.user, self.passwd)

	def list_directory(self, dir_path):
		return self._run_cmd("list_files", dir_path)

	def make_directory(self, dst_dir):
		return self._run_cmd("make_directory", dst_dir)

	def send_file(self, src_file, dst_file):
		return self._run_cmd("send_file", src_file, dst_file )

	def get_file(self, src_file, dst_file):
		return self._run_cmd("get_file", src_file, dst_file )

	def list_snapshots(self):
		return self._run_cmd("get_snapshots")

	def start_process(self, cmd, args=[]):
		return self._run_cmd("start_process", cmd, args)

	def terminate_process(self, pid):
		return self._run_cmd("terminate_process", pid)

	def list_processes(self):
		return self._run_cmd("list_processes")

	#	PRIMITIVES

	def _run_cmd(self, func, *params):
		try:
			with connection(self.vi_src) as c:
				f = getattr(self.vm, func)

				if len(params) is None:
					return f
				else:
					return f( *params )
		except Exception as e:
			print "%s, ERROR: Problem running %s. Reason: %s" % (self.name, func, e)

	def _run_task(self, func, *params):
		
		def wait_for(task):
			s = task.wait_for_state(['success','error'])

			if s == 'error':
				print "DBG ERROR: problem with task %s: %s" % (func, task.get_error_message())
				return False
			return True

		try:
			with connection(self.vi_srv) as c:
				f = getattr(self.vm, func)

				if len(params) is None:
					task = f(sync_run=False)
				else:
					task = f(sync_run=False, *params)
				return wait_for(task)
		except Exception as e:
			print "%s, ERROR: Problem running %s. Reason: %s" % (self.name, func, e)




