import sys
from time import sleep

from ConsoleAPI import API
import socket

import urllib2


host = "rcs-castore"
user = "avmonitor"
passwd = "avmonitorp1234"
connection = None

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

def createNewFactory(target,factory):
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

def checkInstance(target,factory):
    pass

def test():
    print 'test'
    conn = API(host, user, passwd)
    print conn.login()
    operation = conn.operation('AVMonitor')
    target = conn.target_create(operation,'first','first_test')
    print operation, target
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