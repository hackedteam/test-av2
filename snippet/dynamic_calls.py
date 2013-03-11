class vm:

	def power_on(self):
		return "vm is powered on"

	def exec_cmd(self, cmd):
		return "%s executed on vm" % cmd

	def revert_snapshot(self, name):
		return "reverting to snapshot %s" % name

	def task(self, *args):
		return "something goes wrong"

	def three(self, arg1, arg2, arg3, argn):
		return arg1,arg2,arg3,argn

class manager:
	def open_vm(self):
		self.vm = vm()
	
	def __getattr__(self, name):
		f = getattr(vm, name)
		return f

	def revert_last_snapshot(self):
		return self.revert_snapshot("last")

	def _run_task(self, vm, func, args, task=False):
		f = getattr(vm, func)
		if task is True:
			task = f(args)
			return "task: %s" % task
		else:
			return f(args)

	def revert_new_snaphost(self, vm, snapshot):
		return self._run_task(vm, "revert_snapshot", snaphost, task=True)

	def exec_cmd(self, vm, cmd, args):
		return self._run_task(vm, "exec_cmd", cmd, args)

class man:

	def _run_cmd(self, vm, func, params=None, task=False):
		f = getattr(vm, func)

		if task is True:
			if params is None:
				task = f
			else:
				task = f(params)
			return task
		else:
			if params is None:
				return f
			else:
				return f(params)

	def power_on(self, vm):
		return self._run_cmd(vm,"power_on", task=True)

	def execute(self, vm, cmd, args=[]):
		return self._run_cmd(vm, "exec_cmd", [cmd, args])




if __name__ == "__main__":

	vm = vm()

	m = manager()
	print m.revert_last_snapshot()
	print m.exec_cmd(vm,"yoo","gigs")

	n = man()
	print n.power_on(vm)
	print n.execute(vm, "cmd",["arg1","arg2"])


