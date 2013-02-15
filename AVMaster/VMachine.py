import os
from ConfigParser import ConfigParser, NoSectionError

class VMachine:

	def __init__(self, conf_file, name):
		self.name = name
		try:
			self.path = self.getPath(conf_file, name)
			self.snapshot = self.getSnapshot(conf_file, name)	
			self.user = self.getUser(conf_file, name)
			self.passwd = self.getPasswd(conf_file, name)
		except NoSectionError:
			print "[!] VM or VM stuff not found on %s" % conf_file
			
		
	def getPath(self, conf_file, name):
		if not os.path.exists(conf_file):
			return None
			
		config = ConfigParser()
		config.read( conf_file )

		return config.get(name, "path")


	def getSnapshot(self, conf_file, name):
		if not os.path.exists(conf_file):
			return None
			
		config = ConfigParser()
		config.read( conf_file )

		return config.get(name, "snapshot")


	def getUser(self, conf_file, name):
		if not os.path.exists(conf_file):
			return None
			
		config = ConfigParser()
		config.read( conf_file )

		return config.get(name, "user")


	def getPasswd(self, conf_file, name):
		if not os.path.exists(conf_file):
			return None
			
		config = ConfigParser()
		config.read( conf_file )

		return config.get(name, "passwd")

		
	def __str__(self):
		return "%s" % self.name
		
		
