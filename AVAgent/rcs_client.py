import urllib2
from urllib2 import HTTPError
import cookielib
import json
import traceback
from time import sleep
from StringIO import StringIO
import gzip

import os
import sys
import inspect

#pp = pprint.PrettyPrinter(indent=4)
if ".." not in sys.path:
    sys.path.insert(0, "..")

from AVCommon.logger import logging

class Rcs_client:
    myid = "0"

    def __init__(self, host, user="avtest", passwd="avtest"):
        self.host = host
        self.user = user
        self.passwd = passwd

        if 'logging' not in globals():
            from AVCommon.logger import logging
            globals()['logging']=logging
        #self.cookie = self.do_login

    def _get_response(self, link, cookies=None):
        """ Basic HTTP Request/Response with Cookie
        @param link
        @param cookie
        @returns response page
        """
        try:
            print "calling link: %s" % link
            req = urllib2.Request(link)
            req.add_header('Accept-encoding', 'gzip')

            if cookies:
                opener = urllib2.build_opener(
                    urllib2.HTTPCookieProcessor(cookies))
            response = opener.open(req)

            if response.info().get('Content-Encoding') == 'gzip':
                buf = StringIO( response.read())
                f = gzip.GzipFile(fileobj=buf)
                data = f.read()
            else:
                data = response.read()

            sleep(1)
            return data
        except HTTPError as e:
            logging.error("ERROR: processing %s: %s, %s" % (link, e, e.read()))
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
                                          urllib2.HTTPHandler())
            req = urllib2.Request(link, data)
            resp = opener.open(req).read()
            sleep(1)
            return resp
        except HTTPError as e:
            logging.error("ERROR: processing %s: %s, %s" % (link, e, e.read()))
            raise e

    def _call_post(self, api_name, data={}, binary=False, argjson=True):
        link = 'https://%s/%s' % (self.host, api_name)
        logging.debug("_call: %s" % link)
        #logging.debug("binary %s, argjson %s" % (binary, argjson))
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
            logging.error("ERROR: %s" % e)
            logging.debug("DBG trace %s" % traceback.format_exc())
            logging.debug("call error: %s" % resp)
            raise e

    def _call_get(self, api_name):
        link = 'https://%s/%s' % (self.host, api_name)
        logging.debug("_call_get: %s" % link)
        resp = self._get_response(link, self.cookie)
        result = json.loads(resp)
        return result

    def login(self):
        """ Do Login request to catch cookie
        @param link: url to login page
        @param data: post data
        @returns cookie
        """
        login = {'user': self.user,
                 'pass': self.passwd,
                 'version': 2013031101}

        link = "https://%s/auth/login" % self.host
        data = json.dumps(login)
        cj = cookielib.CookieJar()
        resp = self._post_response(link, cj, data)
        result = json.loads(resp)
        # logging.debug(result)
        self.myid = result['user']['_id']
        # logging.debug("my id = %s" % self.myid)

        self.cookie = cj
        return cj


    def logged_in(self):
        return self.cookie is not None

    def logout(self):
        """ Logout for session
        @param session cookie
        @return True/False
        """
        self._call_post('auth/logout')
        return True

    def server_status(self):
        status = self._call_get('status/counters')
        return status

    def disable_analysis(self):
        ret = self._call_post('agent/disable_analysis')
        return ret

    def operation(self, operation):
        """ gets the operation id of an operation """
        operations = self._call_get('operation')
        #logging.debug("DBG operation: %s" % operations)
        ret = [(op['_id'], op['group_ids'][0])
               for op in operations if op['name'] == operation]
        return ret[0] if ret else (None, None)

    def targets(self, operation_id, target=None):
        """ gets the targets id of an operation, matching the target name """
        targets = self._call_get('target')
        #logging.debug("targets: %s" % targets)
        #pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(targets)
        if target:
            ret = [op['_id']
                   for op in targets if op['name'] == target and op['path'][0] == operation_id]
        else:
            ret = [op['_id']
                   for op in targets if op['path'][0] == operation_id]
        return ret

    def all_factories(self):
        """ gets the factories """
        factories = self._call_get('factory')

        # pp.pprint(factories)
        ret = [(op['_id'], op['ident'], op['path'])
               for op in factories]
        return ret

    def factories(self, target_id, all_factories=None):
        """ gets the factories of an operation, matching the target id """
        if not all_factories:
            all_factories = self.all_factories()

        # pp.pprint(factories)
        ret = [(op[0], op[1])
               for op in all_factories if target_id in op[2]]
        return ret

    def instances(self, ident):
        """ gets the instances id of an operation, matching the ident """
        agents = self._call_get('agent')
        # instances: [{u'status': u'open', u'scout': False, u'good': True, u'name': u'avtagent_desktop_windows_elite_silent (1)', u'platform': u'windows', u'demo': False, u'_kind': u'agent', u'stat': {u'grid_size': 183088, u'last_sync': 1386874247, u'source': u'172.20.20.151', u'user': u'avtest', u'device': u'AVTAGENT', u'last_sync_status': 0, u'size': 34599}, u'upgradable': False, u'instance': u'7f198461c7ce800381480345cc5d8617b3015c89', u'ident': u'RCS_0000057058', u'version': 2013103102, u'path': [u'51224a314e091305b800005d', u'52a895cc4e0913f2e600b406'], u'_id': u'52aa04d14e0913a56300c604', u'type': u'desktop', u'desc': u'made by vmavtestat at Thu Dec 12 19:46:32 2013'}]
        # pp.pprint(agents)
        ret = [op['_id'] for op in agents if ident in op['ident'] and op['_kind'] == 'agent']
        return ret

    def instances_by_target_id(self, target_id):
        """ gets the instances id of an operation, matching the ident """
        logging.debug("lookin for instances with target: %s" % target_id)
        agents = self._call_get('agent')
        #logging.debug("agents: %s" % agents)
        #pp.pprint(agents)
        ret = [op for op in agents if target_id in op['path'] and op['_kind'] == 'agent']
        return ret

    def instances_by_name(self, name):
        """ gets the instances id of an operation, matching the ident """
        logging.debug("lookin for instances with target: %s" % name)
        agents = self._call_get('agent')
        logging.debug("agents: %s" % agents)
        #pp.pprint(agents)
        ret = [op for op in agents if name in op['name'] and op['_kind'] == 'agent']
        return ret

    def agents(self, target_id):
        """ gets the agents (agents and factories) of an operation, matching the target id """
        agents = self._call_get('agent')
        # pp.pprint(agents)
        ret = [(op['_id'], op['ident'], op['name'])
               for op in agents if target_id in op['path']]
        return ret

    # user list : verifica presenza utente
    # add group to user
    def user_create(self, name, password, privs, group_id):
        """ Create a user """
        logging.debug("user_create: %s, %s, %s" % (name, password, group_id))
        try:
            data = {'name': name, 'pass': password, 'group_ids':
                [group_id], 'privs': privs, 'enabled': True}
            user = self._call_post('user/create', data)
            return user['_id']
            # return True
        except HTTPError as e:
            if e.code == 409:
                return True
            logging.error(e)
            return False

    def target_delete(self, target_id):
        """ Delete a given target """
        return self._call_post('target/destroy', {'_id': target_id})

    def target_create(self, operation_id, name, desc):
        """ Create a given target """
        data = {'name': name, 'desc': desc, 'operation': operation_id}
        target = self._call_post('target/create', data)
        return target['_id']

    def factory_create(self, operation_id, target_id, ftype, name, desc):
        """ Create a factory """
        data = {'name': name, 'desc': desc, 'operation':
            operation_id, 'target': target_id, 'type': ftype}
        factory = self._call_post('agent/create', data)
        return factory['_id'], factory['ident']

    def factory_add_config(self, factory_id, config):
        """ adds a config to a factory """
        data = {'_id': factory_id, 'config': config}
        return self._call_post('agent/add_config', data)

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
                # logging.debug(fct)
            addlink = '%s/agent/add_config' % base
            f = open(conf_file, 'r')
            cnf = f.read()
            data = {'_id': fct["_id"], 'config': cnf}
            # logging.debug(data)
            resp = self._post_response(addlink, self.cookie, json.dumps(data))

            return True
        except Exception as e:
            logging.debug("DBG trace %s" % traceback.format_exc())
            logging.error(e)
            return False

    def instance_upgrade(self, instance_id, force_soldier = False):
        params = {'_id': instance_id}
        if force_soldier:
            params["force"] = "soldier"
        logging.debug("upgrade: %s" % params)
        try:
            self._call_post('agent/upgrade', params)
            return True
        except:
            return False

    def instance_can_upgrade(self, instance_id):
        try:
            value = self._call_get('agent/can_upgrade/%s' % instance_id)
            return value
        except:
            logging.exception("cannot get can_upgrade")
            return False

    def instance_level(self, instance_id):
        params = {'_id': instance_id}
        try:
            info = self.instance_info(instance_id)
            return info["level"]
        except:
            return False

    def instance_info(self, instance_id):
        agents = self._call_get('agent')
        # pp.pprint(agents)
        ret = [op for op in agents if op['_id'] == instance_id]
        return ret[0] if ret else None

    def instance_close(self, instance_id):
        params = {'_id': instance_id, 'status': 'closed'}
        self._call_post('agent/update', params)

    def instance_delete(self, instance_id):
        """ Delete a given instance
        @param instance
        """
        data = {'_id': instance_id, 'permanent': True}
        return self._call_post('agent/destroy', data)
        # logging.debug(resp)

    def blacklist(self):
        return self._call_post('agent/blacklist')

    def _evidences(self, target):
        pass

    def evidences(self, target_id, instance_id, filter_type=None, filter_value=None):
        """ Get evidences of given agent and target
        @param target
        @param agent
        @param type (if None all types should be returned)

        date: '24h' 'week' 'month' 'now'
        dr e da sono per il :date
        gli altri sono per il :from :to
        dr -> date received, da -> date acquired

        """
        logging.debug("evidences: %s,%s,%s,%s" %(target_id, instance_id, filter_type, filter_value))
        if filter_type and filter_value:
            f = {filter_type: filter_value, "target": target_id, "agent": instance_id, 'date':'dr'}

        else:
            f = {"target": target_id, "agent": instance_id, 'date':'dr'}

        filter = urllib2.quote(json.dumps(f))
        link = 'https://%s/evidence?filter=%s' % (self.host, filter)

        resp = self._get_response(link, self.cookie)
        result = json.loads(resp)
        logging.debug("results: " % result)
        return result


    def build(self, factory, params, out_file):
        """ Build Silent Exe
        @param param_file
        @param factory
        @param out_file
        """

        params['factory'] = {"_id": "%s" % factory}
        # logging.debug("+ Build params: \n%s" % params)

        resp = self._call_post('build', params, binary=True)

        out = open(out_file, 'wb')
        out.write(resp)

        # logging.debug("+ %s bytes saved to %s" % (len(out),  out_file))

    def build_melt(self, factory, params, melt_file, out_file):
        """ Build Melted Exe
        @param param_file
        @param factory
        @param out_file
        """

        params['factory'] = {"_id": "%s" % factory}

        f = open(melt_file, "rb")
        payload = f.read()
        logging.debug("DBG payload size: %s file:  %s" % ( len(payload), melt_file))
        melt_id = self._call_post('upload', payload, binary=True, argjson=False)
        logging.debug("DBG uploaded:  %s" % melt_id)

        params['melt']['input'] = melt_id
        #:  Build: melting: {"admin"=>false, "bit64"=>true, "codec"=>true, "scout"=>true, "input"=>"4f60909baef1de0e4800000a-1361192221.897401094"}

        logging.debug("DBG Build melt params: \n%s" % params)
        #link  = 'https://%s/build' % self.host
        #resp = self.post_response(link, json.dumps(params))
        resp = self._call_post('build', params, binary=True)

        out = open(out_file, 'wb')
        out.write(resp)


