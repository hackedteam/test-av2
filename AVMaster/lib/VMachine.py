import os
from ConfigParser import ConfigParser, NoSectionError

class VMachine:

	def __init__(self, conf_file, name):
		self.name = name
		try:
			self.path = self._getPath(conf_file, name)
			self.snapshot = self._getSnapshot(conf_file, name)	
			self.user = self._getUser(conf_file, name)
			self.passwd = self._getPasswd(conf_file, name)
		except NoSectionError:
			print "[!] VM or VM stuff not found on %s" % conf_file
			
		
	def _getPath(self, conf_file, name):
		if not os.path.exists(conf_file):
			return None
			
		config = ConfigParser()
		config.read( conf_file )
		
		#repo = config.get("vsphere", "repository")
		#return "%s Win7-%s/Win7-%s.vmx" % repo
		
		return config.get(name, "path")


	def _getSnapshot(self, conf_file, name):
		if not os.path.exists(conf_file):
			return None
			
		config = ConfigParser()
		config.read( conf_file )

		return config.get(name, "snapshot")


	def _getUser(self, conf_file, name):
		if not os.path.exists(conf_file):
			return None
			
		config = ConfigParser()
		config.read( conf_file )

		return config.get(name, "user")


	def _getPasswd(self, conf_file, name):
		if not os.path.exists(conf_file):
			return None
			
		config = ConfigParser()
		config.read( conf_file )

		return config.get(name, "passwd")

		
	def __str__(self):
		return "%s" % self.name
		
		
