import os
from ConfigParser import ConfigParser, NoSectionError

class VMachine:
	def __init__(self, conf_file, name):
		self.name = name
		try:
			self.config = ConfigParser()
			self.config.read( conf_file )
			self.path     = self.config.get("vms", name)
			self.snapshot = self.config.get("vm_config", "snapshot")
			self.user     = self.config.get("vm_config", "user")
			self.passwd   = self.config.get("vm_config", "passwd")

		except NoSectionError:
			print "[!] VM or VM stuff not found on %s" % conf_file
		
	def __str__(self):
		return "%s" % self.name

	def __getattr__(self, name):
		#vmman.__call__(name)
		def foo(args):
			print "test : %s, %s" % (name, args)
		return foo

		
if __name__ == "__main__" :

	vm = VMachine("../conf/vms.conf", "panda")
	print vm.test
	vm.test("ciao")
