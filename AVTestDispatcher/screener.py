import subprocess
import os
import shutil
import hashlib, md5
import string, random
from time import sleep
from threading import Thread

from lib.cuckoo.common.exceptions import CuckooAnalysisError, CuckooMachineError, CuckooGuestError
from lib.cuckoo.common.utils import File

class Screener(Thread):
    
    # path to save screens
    # path vmrun
    def __init__(self, vmrun, vm_path, username, password, shot_path):
        Thread.__init__(self)
        self.lock_file = None
        self.vmrun = vmrun
        self.vm_path = vm_path
        self.username = username
        self.password = password
        self.shot_path = shot_path
        
    #def do_start(self, vm_path, username, password, shot_path):
    def run(self):
        idx = 1
        # creating a file .pid
        #self.lock_file = '/tmp/lock.pid'
        #self.lock_file = 'C:\\WINDOWS\Temp\\lock.pid'
        self.lock_file = 'C:\\Users\\avtest\\Documents\\lock.pid'
        if not os.path.exists(self.lock_file):
            lock = open(self.lock_file, 'w')
            lock.write("\n\n")
            lock.close()
        
        #first = "%s/%s.png" % (self.shot_path.replace(' ','\ '), "".join(random.sample(string.letters, 5)))
        if not os.path.exists(self.shot_path + "/shots"):
            os.mkdir(self.shot_path + "/shots")
        #first = u"%s/shots/%s.png" % (self.shot_path, "".random.sample(string.letters, 5))
        first = self.shot_path + "/shots/0000.png"
        self.proc = subprocess.Popen([self.vmrun,
                                    "-h", "https://vcenter5.hackingteam.local/sdk",
                                    "-u", "avtest", "-p", "Av!Auto123",
                                    "-gu", "%s" % self.username,
                                    "-gp", "%s" % self.password,
                                    "captureScreen",
                                    self.vm_path,
                                    first])
        #try:
        #    first_hash = File(first).get_md5()
        #except  (IOError, shutil.Error) as e:
        #    raise CuckooAnalysisError("Unable get md5 for file \"%s\", analysis aborted" % first)
        #    pass

        while True:  
            """ Screenshotting time"""
            if not os.path.exists(self.lock_file):
                print "stopping time"
                break
            # Take screenshot
            # TODO: 
            # username, password of guest account
            if idx < 10:
                cur = self.shot_path + "/shots/000" + str(idx) + ".png"
            elif idx > 9:
                cur = self.shot_path + "/shots/00" + str(idx) + ".png"    

            self.proc = subprocess.Popen([self.vmrun,
                                        "-h", "https://vcenter5.hackingteam.local/sdk",
                                        "-u", "avtest", "-p", "Av!Auto123",
                                        "-gu", "%s" % self.username,
                                        "-gp", "%s" % self.password,
                                        "captureScreen",
                                        self.vm_path,
                                        cur])
            # 2. md5 of file
            #try:
            #    cur_hash = File(cur).get_md5()
            #except  (IOError, shutil.Error) as e:
            #    raise CuckooAnalysisError("Unable get md5 for file \"%s\", analysis aborted" % cur)
            #    pass
                            
            # 3. if md5 current == previous delete file
            #if cur_hash == first_hash:
            #    print "removing current snapshot"
            #    os.remove(cur)
            
            # 4. sleeping time
            idx+=1
            sleep(1)
    
    
    def stop(self):
        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)

