import sys
from time import sleep

from ConsoleAPI import API
import socket

import urllib2
import zipfile
import os.path


host = "rcs-castore"
user = "avmonitor"
passwd = "avmonitorp1234"
connection = None

def unzip(filename):
    zfile = zipfile.ZipFile(filename)
    for name in zfile.namelist():
      (dirname, filename) = os.path.split(name)
      print "Decompressing " + filename + " on " + dirname
      if not os.path.exists(dirname) and dirname:
        os.mkdir(dirname)
      fd = open(name,"w")
      fd.write(zfile.read(name))
      fd.close()

def internet_off():
    ips = [ '87.248.112.181', '173.194.35.176', '176.32.98.166']

    ret = False
    for rep in ips:
        try:
            l(rep)
            response=urllib2.urlopen('http://' + rep, timeout=5)
            return False
        except urllib2.URLError as err:
            ret = True
    return ret

def l(message):
    print message

def produceOutput(message):
    l(message)

def createNewFactory(target, factory):
    id = connection.get_target_id(target)
    l(id)

def copyConfig(config):
    pass

def buildAgent(kind):
    pass
    
def executeBuild():
    pass

def mouseMove():
    pass

def checkInstance(target, factory):
    pass

def test():
    print 'test'
    conn = API(host, user, passwd)
    print conn.login()

    if(False):
        operation, target, factory = '511dfd70aef1de05f8001090', '511e44d4aef1de05f800137a', '511e44d5aef1de05f8001380'

    else:
        operation = conn.operation('AVMonitor')
        target = conn.target_create(operation,'Turca','la mia targa')
        factory = conn.factory_create(operation, target, 'desktop', 'fattoria', 'degli animali')
        print "factory: ", factory
        #sleep(10)

        config = open('assets/basic_config_castore.json').read()
        conn.factory_add_config(factory, config)

    param = { 'platform': 'windows',
          'binary': { 'demo' : False, 'admin' : False},
          'melt' : {'scout' : True, 'admin' : False, 'bit64' : True, 'codec' : True },
          'sign' : {}
          }

    #{"admin"=>false, "bit64"=>true, "codec"=>true, "scout"=>true}
    try:
        r = conn.build(factory, param, 'build.out')
    except Exception, e:
        print e
    
    unzip('build.out')

    #sleep(5)
    conn.target_delete(target)
    print operation, target, factory
    print conn.logout()

def main():
    if(sys.argv.__contains__('test')):
        test()
        exit(0)
    
    if not internet_off():
        produceOutput("ERROR: I don't want to reach Internet")
        #exit(0)

    l("Network unreachable")
    hostname = socket.gethostname()
    l(hostname)

    target = hostname
    factory = hostname
    config = "config.json"

    self.connection = API(host, user, passwd)
    
    createNewFactory(target,factory)
    copyConfig(config)
    buildAgent("silent")
    executeBuild()
    #sleep(60 * 5)
    mouseMove()
    #sleep(60)
    checkInstance(target,factory)

    self.connection.do_logout()



if __name__ == "__main__":
    main()