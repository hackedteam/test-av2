import sys
from time import sleep
import time

from ConsoleAPI import API
import socket

import urllib2
import zipfile
import os.path

import subprocess

def unzip(filename):
    zfile = zipfile.ZipFile(filename)
    names = []
    for name in zfile.namelist():
        (dirname, filename) = os.path.split(name)
        print "Decompressing " + filename + " on " + dirname
        #if not os.path.exists(dirname) and dirname:
        #    os.mkdir(dirname)
        #fd = open(name,"w")
        #fd.write(zfile.read(name))
        #fd.close()
        zfile.extract(name)
        names.append(name)
    return names

def internet_off():
    ips = [ '87.248.112.181', '173.194.35.176', '176.32.98.166']

    ret = False
    for rep in ips:
        try:
            print rep
            response=urllib2.urlopen('http://' + rep, timeout=5)
            return False
        except urllib2.URLError as err:
            ret = True
    return ret

def wait_timeout(proc, seconds):
    """Wait for a process to finish, or raise exception after timeout"""
    start = time.time()
    end = start + seconds
    interval = min(seconds / 1000.0, .25)

    print "wait for: %s sec" % seconds
    while True:
        result = proc.poll()
        if result is not None:
            return result
        if time.time() >= end:
            proc.kill()
            print "Process timed out, killed"
            break;
        time.sleep(interval)

class VMAVTest:
    host = "rcs-castore"
    user = "avmonitor"
    passwd = "avmonitorp1234"
    connection = None

    def create_new_factory(self, operation, target, factory, config):
        c = self.connection
        operation = c.operation(operation)
        print "operation: " , operation

        #TODO: delete target if exists
        targets = c.targets(operation, target)
        print "targets: ",  targets
        #for t in targets:
        #    c.target_delete(target)

        target = c.target_create(operation, target, 'made by vmavtest at %s' % time.ctime())
        factory = c.factory_create(operation, target, 'desktop', factory, 'made by vmavtestat at %s' % time.ctime())

        conf = open(config).read()
        c.factory_add_config(factory, conf)
        print "factory: ", factory
        return factory

    def build_agent(self, factory, demo = False):
        c = self.connection
        param = { 'platform': 'windows',
              'binary': { 'demo' : demo, 'admin' : False},
              'melt' : {'scout' : True, 'admin' : False, 'bit64' : True, 'codec' : True },
              'sign' : {}
              }

        #{"admin"=>false, "bit64"=>true, "codec"=>true, "scout"=>true}
        try:
            filename = 'build.zip'
            if os.path.exists(filename):
                os.remove(filename)
            r = c.build(factory, param, filename)
            contentnames = unzip(filename)
            print "contents: %s" % contentnames
            return [n for n in contentnames if n.endswith('.exe')]
        except Exception, e:
            print "Error: ", e
            raise e
        
    def execute_build(self, exenames):
        for exe in exenames:
            print "execute: " + exe
            subp = subprocess.Popen([exe])

    def mouse_move(self, timeout=10):
        subp = subprocess.Popen(['mouse_emu.exe'])
        wait_timeout(subp, timeout)

    def check_instance(self, factory):
        c = self.connection
        return c.enum_instances(factory)

    def report_results(self, results):
        r=open("results.txt", "w+")
        r.write(result)
        r.close()
        
    def execute_av(self):
        hostname = socket.gethostname()
        print "%s %s\n" % (hostname, time.ctime())
        
        if not internet_off():
            print "ERROR: I don't want to reach Internet"
        #exit(0)

        print "Network unreachable"
       

        print "Hostname: ", hostname
        operation = 'AVMonitor'
        target = hostname
        factory = hostname
        config = "config.json"

        self.connection = API(self.host, self.user, self.passwd)
        self.connection.login()
        try:
        
            factory = self.create_new_factory(operation, target, factory, config)
            exe = self.build_agent( factory, demo=True )
            self.execute_build(exe)
            print "wait for 6 minutes"
            sleep(60 * 6)
            print "move mouse for 10 seconds"
            self.mouse_move()
            print "wait for 1 minute"
            sleep(60 * 1)
            result = self.check_instance( factory )

        except Exception, e:
            print "Error: ", e
            raise e
        finally:
            self.connection.logout()

def test_mouse():
    print "test mouse"
    subp = subprocess.Popen(['notepad.exe'])
    wait_timeout(subp,3)
    print "stop mouse"
    
def main():
    if(sys.argv.__contains__('test')):
        #test_api()
        #test_zip()
        test_mouse()
        exit(0)

    results = 'results.txt'
    if os.path.exists(results):
        os.remove(results)
        
    #sys.stdout = open(results,'w')
    vmavtest = VMAVTest()
    vmavtest.execute_av()

if __name__ == "__main__":
    main()
