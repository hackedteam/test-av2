import sys
from time import sleep
import time
import socket

import urllib2
import zipfile
import os.path

import subprocess
import Queue
import threading

from ConsoleAPI import API

def unzip(filename):
    zfile = zipfile.ZipFile(filename)
    names = []
    for name in zfile.namelist():
        (dirname, filename) = os.path.split(name)
        print "- Decompressing " + filename 
        zfile.extract(name)
        names.append(name)
    return names

def check_internet(address, queue):
    try:
        print "- Check connection to: %s" % address
        response = urllib2.urlopen('http://' + address, timeout = 10)
        queue.put(True)

    except urllib2.URLError as err:
        queue.put(False)


def internet_on():
    ips = [ '87.248.112.181', '173.194.35.176', '176.32.98.166', 'www.reddit.com', 'www.bing.com', 'www.facebook.com']
    q = Queue.Queue()
    for i in ips:
        t = threading.Thread(target = check_internet, args = (i, q) )
        t.daemon = True
        t.start()

    s = [ q.get() for i in ips ]
    return any(s)

def wait_timeout(proc, seconds):
    """Wait for a process to finish, or raise exception after timeout"""
    start = time.time()
    end = start + seconds
    interval = min(seconds / 1000.0, .25)

    print "- wait for: %s sec" % seconds
    while True:
        result = proc.poll()
        if result is not None:
            return result
        if time.time() >= end:
            proc.kill()
            print "- Process timed out, killed"
            break;
        time.sleep(interval)

class VMAVTest:

    user = "avmonitor"
    passwd = "avmonitorp123"
    connection = None

    def __init__(self, host, melt = False):
        self.melt = melt
        self.host = host

    def create_new_factory(self, operation, target, factory, config):
        c = self.connection
        operation_id = c.operation(operation)
        #print "operation: " , operation, "target: ", target

        #TODO: delete target if exists
        targets = c.targets(operation_id, target)
        print "- Delete targets: ",  targets
        for t in targets:
            c.target_delete(t)

        target = c.target_create(operation_id, target, 'made by vmavtest at %s' % time.ctime())
        factory = c.factory_create(operation_id, target, 'desktop', factory, 'made by vmavtestat at %s' % time.ctime())

        with open(config) as f:
            conf = f.read()
        conf = conf.replace('$(HOSTNAME)', self.host)
        c.factory_add_config(factory, conf)

        print "open config to write"
        with open('build/config.actual.json','wb') as f:
            f.write(conf)

        #print "factory: ", factory
        return factory

    def build_agent(self, factory, melt = None, demo = False):
        c = self.connection
        param = { 'platform': 'windows',
              'binary': { 'demo' : demo, 'admin' : False},
              'melt' : {'scout' : True, 'admin' : False, 'bit64' : True, 'codec' : True },
              'sign' : {}
              }

        #{"admin"=>false, "bit64"=>true, "codec"=>true, "scout"=>true}
        try:
            
            filename = 'build/build.zip'
            if os.path.exists(filename):
                os.remove(filename)

            if melt:
                print "- Melt build with: ", melt
                r = c.build_melt(factory, param, melt, filename)
            else:
                print "- Silent build"
                r = c.build(factory, param, filename)

            contentnames = unzip(filename)
            #print "contents: %s" % contentnames
            return [n for n in contentnames if n.endswith('.exe')]
        except Exception, e:
            print "Error: ", e
            raise e
        
    def execute_build(self, exenames):
        for exe in exenames:
            print "- execute: " + exe
            subp = subprocess.Popen([exe])

    def mouse_move(self, timeout=10):
        subp = subprocess.Popen(['assets/keyinject.exe'])
        wait_timeout(subp, timeout)

    def check_instance(self, factory):
        c = self.connection
        return c.enum_instances(factory)
        
    def execute_av(self):
        hostname = socket.gethostname()
        print "%s %s\n" % (hostname, time.ctime())

        print "- Hostname: ", hostname
        operation = 'AVMonitor'
        target = 'VM_%s' % hostname
        factory = hostname
        config = "assets/config.json"

        self.connection = API(self.host, self.user, self.passwd)
        self.connection.login()
        try:
            if not os.path.exists('build'):
                os.mkdir('build')
            factory = self.create_new_factory(operation, target, factory, config)

            meltfile = None
            if self.melt:
                meltfile = 'assets/meltapp.exe'

            exe = self.build_agent( factory, meltfile )

            self.execute_build(exe)
            print time.ctime(), "- wait for 6 minutes"
            sleep(60 * 6)
            print time.ctime(), "- move mouse for 10 seconds"
            self.mouse_move()
            print time.ctime(), "- wait for 1 minute"
            sleep(60 * 1)
            result = self.check_instance( factory )
            print "- Result: ", result

        except Exception, e:
            print "Error: ", e
            raise e
        finally:
            self.connection.logout()

def test_internet():
    print internet_off()

def test_mouse():
    print "test mouse"
    sleep(10)
    subp = subprocess.Popen(['assets/keyinject.exe'])
    wait_timeout(subp, 3)
    print "stop mouse"

def test_multithread():
    ips = [ '87.248.112.181', '173.194.35.176', '176.32.98.166', 'www.reddit.com', 'www.bing.com', 'www.facebook.com']
    
    q = Queue.Queue()
    for i in ips:
        t = threading.Thread(target=check_internet, args=(i, q) )
        t.daemon = True
        t.start()

    s = [ q.get() for i in ips ]
    print s
    

def main():
    if(sys.argv.__contains__('test')):
        test_multithread()
        #test_internet()
        exit(0)

    if internet_on():
        print "== ERROR: I reach Internet =="
        exit(0)

    print "- Network unreachable"


    melt = False
    if len(sys.argv) == 3:
        server, kind = sys.argv[1:3]
        
        if kind == "melt":
            melt = True
    else:
        server = "rcs-minotauro"
    
    results = 'results.txt'
    if os.path.exists(results):
        os.remove(results)
        
    print "- Server: ", server, " Melt: ", melt
    vmavtest = VMAVTest(server, melt )
    vmavtest.execute_av()

if __name__ == "__main__":
    main()
