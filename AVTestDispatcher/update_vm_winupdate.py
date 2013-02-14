import subprocess
import ConfigParser
import sys

class Config:
	def __init__(self, conf):
		self.conf = ConfigParser.ConfigParser()
        self.file = conf
        
    def getVmx(self, vm):
        self.conf.read(self.file)
        vmx = self.conf.get(vm, 'label')
        return vmx
    
    def getVmrunPath(self):
        self.conf.read(self.file)
        path = self.conf.get('vmware','path')
        return path
        
    def getMachines(self):
        self.conf.read(self.file)
        vms = self.conf.get('vmware', 'machines').split(",")
        return vms

class Command:
    def __init__(self, vmx, path):
        self.vmx = vmx
        self.path = path
        
    def show(self):
        sys.stdout.write("\r\nshowing all stuff:\nvmx: %s\npath: %s" % (self.vmx, self.path))


if __name__ == "__main__":
    #config_file = "c:/test-av/conf/vmware.conf"
    config_file = "conf/vmware.conf"
    
    conf = Config(config_file)
    vms = conf.getMachines()
    exe = conf.getVmrunPath()
    
    


