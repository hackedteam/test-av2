class vm:
	def __init__(self):
		print "diopor"

	def power_on(self):
		return "vm is powered on"

class manager:
	def open_vm(self):
		self.vm = vm

	def __getattr__(self, name):
		f = getattr(self.vm, name)
		f()

if __name__ == "__main__":

	m = manager()
	m.open_vm()
	m.power_on()
