from time import sleep
from datetime import datetime
from pysphere import VIServer


class vSphereManager:
	def __init__(self, host, user, passwd):
		self.hostname = host
		self.username = user
		self.password = passwd
		self.server = VIServer()

	def connect(self):
		# add trace_file=True to debug SOAP request/response
		self.server.connect(self.hostname, self.username, self.password)

	def _run_cmd(self, vm, func, task, *params):
		try:
			f = getattr(vm, func)

			if task is True:
				if len(params) is None:
					task = f(sync_run=False)
				else:
					task = f(sync_run=False, *params)
				return task
			else:
				if len(params) is None:
					return f
				else:
					return f( *params )
		except Exception as e:
			print "%s, ERROR: Problem running %s. Reason: %s" % (vm.get_property('name'), func, e)

	def get_vm(self, vm_path):
		return self.server.get_vm_by_path(vm_path)

	def power_on(self, vm):
		return self._run_cmd(vm, "power_on", True)

	def power_off(self, vm):
		return self._run_cmd(vm, "power_off", True)

	def suspend(self, vm):
		return self._run_cmd(vm, "power_on", True)

	def login_in_guest(self, vm, user, passwd):
		return self._run_cmd(vm, "login_in_guest", False, user, passwd)

	def make_directory(self, vm, dst_dir):
		return self._run_cmd(vm, "make_directory", False, dst_dir)

	def send_file(self, vm, src_file, dst_file):
		return self._run_cmd(vm, "send_file", False, src_file, dst_file )

	def get_snapshots(self, vm):
		return self._run_cmd(vm, "get_snapshots", True)

	def revert_to_snapshot(self, vm):
		return self._run_cmd(vm, "revert_to_snapshot", True)

	def create_snapshot(self, vm, name):
		return self._run_cmd(vm, "create_snapshot", True, name)

	def delete_snapshot(self, vm, name):
		return self._run_cmd("delete_named_snapshot", True, name)

class oldSphereManager:

	def __init__(self, conf, srv):
		""" vSphere parameters for connections 
		"""
		self.srv    = srv
		self.conf   = conf

	def revert_last_snapshot(self, vm): #vm_name):
		""" Revert to current snapshot
		@params vm_name: virtual machine name
		@returns error or True
		"""
		try:
		    task = vm.revert_to_snapshot(sync_run=False)
		    status = task.wait_for_state(['success','error'])

		    if status == 'error':
		        #return "ERROR: problem reverting snapshot. Reason: %s" % task.get_error_message()
		        return False

		    return True
		except Exception as e:
			print "DBG Error reverting %s. Reason %s" % (vm_name,e)

	def refresh_snapshot(self, vm):
	    task = vm.create_snapshot("%s" % date, sync_run=False)
	    try:
	        s = task.wait_for_state(['success','error'])

	        if s == 'error':
	            print "DBG ERROR: snapshot not created: %s" % task.get_error_message()
	            return False
	        
	        if s == 'success':
	            #delete snapshot!
	            snaps = vm.get_snapshots()

	            t = vm.delete_named_snapshot(snaps[-2].get_name(), sync_run=False)

	            try:
	                s = t.wait_for_state(['success','error'])

	                if s == 'error':
	                    print "DBG ERROR: previous snapshot not deleted: %s" % task.get_error_message()
	                    return False
	            except Exception as e:
	                print "DBG ERROR: cant delete snapshot %s. reason: %s" % (snaps[-2].get_name(),e)
	                return False

	        job_log(vm_name, "UPDATED")
	        return True
	    except Exception as e:
	        print "DBG ERROR: cant refresh snapshot. reason: %s" % e
	        return False


	def startup(self, vm): #vm_name):
		""" startup virtual machine
		@params vm_name: virtual machine name
		@returns bool
		"""
		task = vm.power_on(sync_run=False)
		status = task.wait_for_state(['success','error'])

		if status == 'error':
		    #return "ERROR: problem starting vm. Reason: %s" % task.get_error_message()
		    return False

		return True


	def shutdown(self, vm): #vm_name):
		""" shutdown virtual machine
		@params vm_name: virtual machine name
		@returns bool
		"""        
		#vm = get_vm(vm_name)
		task = vm.power_off(sync_run=False)
		status = task.wait_for_state(['success','error'])

		if status == 'error':
			return False
		return True		


	def suspend(self, vm): #vm_name):
		""" Suspend virtual machine
		@params vm_name: virtual machine name
		@returns bool
		"""
		#vm = get_vm(vm_name)
		task = vm.suspend(sync_run=False)
		status = task.wait_for_state(['success','error'])

		if status == 'error':
			return False
		return True

	def login_in_guest(self, vm):
		""" Does Login in guest 
		@params vm_name
		@returns bool result of operation
		"""
		vm_user = self.conf.get("vm_config", "user")
		vm_pass = self.conf.get("vm_config", "passwd")   

		try:
			vm.login_in_guest(vm_user, vm_pass)
			return True
		except Exception as e:
			print "DBG Exception: %s" % e
			return False	

	def wait_for_login(self, vm, timeout=20):
		c = 0
		logged = self.login_in_guest(vm)
		while logged == False:
			sleep(60)
			c+=1
			logged = self.login_in_guest(vm)
			if c >= timeout:
				return False
		return True


	def copy_files_to_guest(self, vm, src_dir, src_files, dst_dir):
		""" Copy given files to given dir inside guest 
		"""
		memo = []
		
		for src_file in src_files:
			print "time for %s" % src_file
			d,f = src_file.split("/")
			src = "%s/%s/%s" % (src_dir, d, f)

			if d == ".":
				dst = "%s\\%s" % (dst_dir, f)
			else:
				dst = "%s\\%s\\%s" % (dst_dir, d, f)

			rdir = "%s\\%s" % (dst_dir, d)

			if not rdir in memo:
				print "mkdir %s" % (rdir)
				vm.make_directory(rdir)
				memo.append(rdir)

			print "copying %s to %s" % (src, dst)
			vm.send_file(src, dst)

		return True

	def execute_cmd(self, vm, cmd, args=[], timeout=40):
		""" Executes a command and wait max timeout min
		@param vm_name
		@param cmd
		@param args
		@return bool 
		"""
		#vm = get_vm(vm_name)
		pid = vm.start_process(cmd, args=args)

		if pid is not None:
	        
			c = 0
			while c <= timeout:
				found = False
				sleep(60)
				c+=1
				procs = vm.list_processes()

				for p in procs:
					if pid == p['pid']:
						found = True
				if found == False:
					print "DBG process ended"
					#executed = True
					#break
					return True
		else: 
			return False


	def list_processes(self, vm):
		""" Returns a list of processes in guest
		"""
		return vm.list_processes()
