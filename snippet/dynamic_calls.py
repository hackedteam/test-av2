class vm:
	def __init__(self):
		print "portacilapace"

	def power_on(self):
		return "vm is powered on"

	def exec_cmd(self, cmd):
		return "%s executed on vm" % cmd

	def three(self, arg1, arg2, arg3, argn):
		return arg1,arg2,arg3,argn

class manager:
	def open_vm(self):
		self.vm = vm()

	def __getattr__(self, name):
		f = getattr(self.vm, name)
		return f

if __name__ == "__main__":

	m = manager()
	m.open_vm()
	print m.power_on()
	print m.exec_cmd('ls -la')
	print m.three("uno","due","tre","enne")
