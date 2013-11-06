import string
from threading import Thread
from ConfigParser import ConfigParser
from AVAgent.old.puppet import VMachine, Task

conf_file = "vms.cfg"

class Analysis(Thread):
    def __init__(self, analysis_conf_file):
        Thread.__init__(self)
        self.exe_path = self.getExePath(analysis_conf_file)
        self.vmrun_path = self.getVmrunPath(analysis_conf_file)
        self.vms = self.getVms(analysis_conf_file)
        self.status = -1


    def getExePath(self, conf_file):
        config = ConfigParser()
        config.read( conf_file )

        return config.get("analysis", "exe_path")

        
    def getVms(self, conf_file):
        config = ConfigParser()
        config.read( conf_file )
        
        vmss = config.get("analysis", "vms")
        vms = string.split(vmss, ",")

        return vms
    
    def getVmrunPath(conf_file):
        config = ConfigParser()
        config.read( conf_file )
        
        return config.get("analysis", "vmrun_path")
        

    def run(self):
        vms = []
        
        for vm in self.vms:
            v = VMachine(conf_file, vm)
            t = Task(v, self.exe_path, self.vmrun_path)
            t.start()


