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
import argparse

from rcs_client import Rcs_client
import logger

def unzip(filename):
    zfile = zipfile.ZipFile(filename)
    names = []
    for name in zfile.namelist():
        (dirname, filename) = os.path.split(name)
        print "- Decompress: " + filename 
        zfile.extract(name)
        names.append(name)
    return names

def check_internet(address, queue):
    """ True if dns or http are reachable """
    print "- Check connection: %s" % address

    ret = False
    try:    
        #if hasattr(socket, 'setdefaulttimeout'):
        #    socket.setdefaulttimeout(5)
        response = socket.gethostbyaddr( address )
        #print "i resolve dns: ", address
        ret |= True
    except:
        ret |= False

    try:    
        if(ret == False):
            response = urllib2.urlopen('http://' + address, timeout = 10)
            #print "i reach url: ", address
            ret |= True
    except:
        ret |= False

    queue.put(ret)


def internet_on():
    ips = [ '87.248.112.181', '173.194.35.176', '176.32.98.166', 'www.reddit.com', 'www.bing.com', 'www.facebook.com','stackoverflow.com']
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

    print "DBG wait for: %s sec" % seconds
    while True:
        result = proc.poll()
        if result is not None:
            return result
        if time.time() >= end:
            proc.kill()
            print "DBG Process timed out, killed"
            break;
        time.sleep(interval)

class VMAVTest:

    user = "avmonitor"
    passwd = "avmonitorp123"
    connection = None

    def __init__(self, backend, frontend, kind):
        self.kind = kind
        self.host = (backend, frontend)

    def delete_targets(self, operation):
        c = Rcs_client(self.host[0], self.user, self.passwd)
        
        c.login()
        operation_id = c.operation(operation)
        print "operation_id: %s" % operation_id
        targets = c.targets(operation_id)
        for t_id in targets:
            print "- Delete target: %s" % t_id
            c.target_delete(t_id) 
        c.logout()


    def create_new_factory(self, operation, target, factory, config):
        c = self.connection
        operation_id = c.operation(operation)
        print "DBG operation: " , operation, " target: ", target, " factory: ", factory

        # gets all the target with our name in an operation
        targets = c.targets(operation_id, target)

        if len(targets) > 0:
            # keep only one target
            for t in targets[1:]:
                c.target_delete(t)    

            target_id = targets[0]
            
            #print "target_id: ", target_id
            agents = c.agents( target_id )

            for agent_id, ident, name in agents:
                print "DBG   ", agent_id, ident, name
                if name.startswith(factory):
                    print "- Delete instance: %s %s" % (ident, name)
                    c.instance_delete(agent_id)
        else:
            print "- Create target: %s" % target
            target_id = c.target_create(operation_id, target, 'made by vmavtest at %s' % time.ctime())
        factory_id, ident = c.factory_create(operation_id, target_id, 'desktop', factory, 'made by vmavtestat at %s' % time.ctime())

        with open(config) as f:
            conf = f.read()
        conf = conf.replace('$(HOSTNAME)', self.host[1])
        c.factory_add_config(factory_id, conf)

        #print "open config to write"
        with open('build/config.actual.json','wb') as f:
            f.write(conf)

        #print "factory: ", factory
        return (target, factory_id, ident)

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

            print "+ SUCCESS GHOST BUILD"
            return [n for n in contentnames if n.endswith('.exe')]
        except Exception, e:
            print "+ FAILED GHOST BUILD: "
            raise e
        
    def execute_build(self, exenames):
        try:
            exe = exenames[0]
            print "- Execute: " + exe
            subp = subprocess.Popen([exe])
            print "+ SUCCESS GHOST EXECUTE"
        except Exception, e:
            print "+ FAILED GHOST EXECUTE"
            raise e

    def mouse_move(self, timeout=10):
        subp = subprocess.Popen(['assets/keyinject.exe'])
        wait_timeout(subp, timeout)

    def check_instance(self, ident):
        c = self.connection
        instances = c.instances( ident )
        print "DBG instances: %s" % instances
        if len(instances) > 0:
            print "+ SUCCESS GHOST SYNC"
            return True
        else:
            print "+ FAILED GHOST SYNC"
            return False
        
    def execute_av(self):
        hostname = socket.gethostname()
        print "- Host: %s %s\n" % (hostname, time.ctime())
        operation = 'AVMonitor'
        target = 'VM_%s' % hostname
        factory ='%s_%s' % (hostname, self.kind)
        config = "assets/config.json"

        self.connection = Rcs_client(self.host[0], self.user, self.passwd)
        self.connection.login()
        try:
            if not os.path.exists('build'):
                os.mkdir('build')
            target_id, factory_id, ident = self.create_new_factory(operation, target, factory, config)

            meltfile = None
            if self.kind == 'melt':
                meltfile = 'assets/meltapp.exe'

            exe = self.build_agent( factory_id, meltfile )

            self.execute_build(exe)
            print "- Wait for 6 minutes: %s" % time.ctime() 
            sys.stdout.flush()

            sleep(60 * 6)

            print "- Move mouse for 30 seconds"
            sys.stdout.flush()
            self.mouse_move(timeout = 30)

            print "- wait for 1 minute: %s" % time.ctime() 
            sys.stdout.flush()
            
            sleep(60 * 1)
            
            result = self.check_instance( ident )
            print "- Result: ", result

        except Exception, e:
            print "ERROR: ", e
            raise e
        finally:
            self.connection.logout()

def internet(args):
    print time.ctime()
    print "internet on: ", internet_on()
    print time.ctime()

def clean(args):
    operation = 'AVMonitor'
    print "- Server: %s/%s %s" % (args.backend,args.frontend, args.kind)
    vmavtest = VMAVTest( args.backend, args.frontend , args.kind )
    vmavtest.delete_targets(operation)

def scout(args):
    if socket.gethostname() != 'zenovm':
        if internet_on():
            print "== ERROR: I reach Internet =="
            exit(0)

    print "- Network unreachable"

    print "- Server: %s/%s %s" % (args.backend,args.frontend, args.kind)
    vmavtest = VMAVTest( args.backend, args.frontend , args.kind )
    vmavtest.execute_av()

def test(args):
    ips = [ '87.248.112.181', '173.194.35.176', '176.32.98.166', 'www.reddit.com', 'www.bing.com', 'www.facebook.com']
    
    q = Queue.Queue()
    for i in ips:
        t = threading.Thread(target=check_internet, args=(i, q) )
        t.daemon = True
        t.start()

    s = [ q.get() for i in ips ]
    print s

    print "test mouse"
    sleep(10)
    subp = subprocess.Popen(['assets/keyinject.exe'])
    wait_timeout(subp, 3)
    print "stop mouse"
    

def main():
    logger.setLogger(debug=False)

    # scout -b 123 -f 123 -k silent/melt
    parser = argparse.ArgumentParser(description='AVMonitor avtest.')

    parser.add_argument('action', choices=['scout', 'internet', 'test', 'clean']) #'elite'
    parser.add_argument('-b', '--backend')
    parser.add_argument('-f', '--frontend')
    parser.add_argument('-k', '--kind', choices=['silent', 'melt'])
    args = parser.parse_args()

    actions = {'scout': scout, 'internet': internet, 'test': test, 'clean': clean}
    actions[args.action](args)
  

if __name__ == "__main__":
    main()
