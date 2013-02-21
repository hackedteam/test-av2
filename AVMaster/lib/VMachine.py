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
		
		
