from scripts.mobile.hardware.apk import apk_dataLoader
from scripts.mobile.hardware.utils import wifiutils, superuserutils, utils

__author__ = 'olli', 'mlosito'

import sys
import socket

sys.path.append("/Users/olli/Documents/work/AVTest/")
sys.path.append("/Users/mlosito/Sviluppo/Rite/")
sys.path.append("/Users/mlosito/Sviluppo/Rite/scripts/mobile/hardware")
sys.path.append("/Users/zeno/AVTest/")

import adb

from AVAgent import build
#from AVCommon import logger
#from AVAgent.build import build


servers = {
    "castore": { "backend": "192.168.100.100",
                 "frontend": "192.168.100.100",
                 "operation": "QA",
                 "target_name": "HardwareFunctional"},
    "polluce": { "backend": "",
                 "frontend": "",
                 "operation": "QA",
                 "target_name": "HardwareFunctional"},
    "zeus": { "backend": "",
              "frontend": "",
              "target_name": "QA",
              "operation": "HardwareFunctional"},
    "minotauro": { "backend": "192.168.100.201",
              "frontend": "192.168.100.204",
              "target_name": "QA",
              "operation": "HardwareFunctional"},
}

params = {
    'platform': 'android',
    'binary': {'demo': False, 'admin': True},
    'sign': {},
    'melt': {}
}


client_context = {}
server_context = {}


def _set_util(context_elements, context):
    for k, v in context_elements.items():
        context[k] = v


def _get_util(context_element, context):
    key = context_element
    if key not in context:
        return "Key not found: %s" % context.keys()
    value = context[key]

    print "key: %s value: %s" % (key, value)
    return value


def get_server(context_element):
    return _get_util(context_element, server_context)


def set_server(context_elements):
    return _set_util(context_elements, server_context)


# Used get_client because 'set' is a builin funciton
def get_client(context_element):
    return _get_util(context_element, client_context)


# Used set_client because 'get' is a builin function
def set_client(context_elements):
    return _set_util(context_elements, client_context)


def dev_is_rooted(device):
    packs = device.shell("pm list packages")
    if "com.noshufou.android.su" in packs or "eu.chainfire.supersu" in packs:
        print "the phone is rooted"
        return True
    return False


"""
    build apk on given server with given configuration
"""
def build_apk(kind, srv, factory):
    class Args:
        pass

    report = None

    try:
        srv_params = servers[srv]
    except KeyError:
        return False


    args = Args()

    args.action = "pull"
    args.platform = "android"
    args.kind = kind
    args.backend = srv_params["backend"]
    args.frontend = srv_params["frontend"]
    args.platform_type = "mobile"
    args.operation = srv_params["operation"]
    args.param = params
    args.asset_dir = "assets"

    # servono??
    args.blacklist = ""
    args.soldierlist = ""
    args.nointernetcheck = socket.gethostname()
    args.puppet = "rite"
    args.factory = factory

    build.connection.host = srv_params["backend"]
    #build.connection.user = "avmonitor"
    build.connection.passwd = "Castorep123"

    results, success, errors = build.build(args, report)
    #print "after build", results, success, errors
    return success


"""
    check evidences on server passed as "backend"
"""
def check_evidences(backend, type_ev, key=None, value=None, imei=None):
#    #backend = command.context["backend"]
#    try:
        build.connection.host = backend
        build.connection.user = "avmonitor"
        build.connection.passwd = "Castorep123"
        #success, ret = build.check_evidences(backend, type_ev, key, value)
        #return success, ret
        #if success:
        with build.connection() as client:
            instance_id, target_id = build.get_instance(client, imei)
            print "instance_id: ", instance_id
            if not instance_id:
                print "instance not found"
                return False, target_id

            evidences = client.evidences(target_id, instance_id, "type", type_ev)
            if evidences:
                return True, evidences
            return False, "No evidences found for that type"
#    except:
#        return False, "Error checking evidences"
#        else:
#            return False, "no evidences found at all"


def do_test():
    assert build_apk("silent","castore"), "Build failed. It have to be succeded."
    assert build_apk("silent","castoro") is False, "Build succeded. It have to dont be succeded."

    print "all done"

if __name__ == "__main__":
    do_test()


# Nota: l'install installa anche l'eventuale configurazione definita nell'apk_dataloader.
# La confiurazione puo' essere definita come singoli files o come zip (ma non entrambi i metodi)
def install(apk_id, dev):
    apk_instance = apk_dataLoader.get_apk(apk_id)
    apk_instance.install(dev)


#Nota: l'install installa anche l'eventuale configurazione definita nell'apk_dataloader.
#La confiurazione puo' essere definita come singoli files o come zip (ma non entrambi i metodi)
def install_agent(dev):
    install('agent', dev)


#Nota: (per l'agente fa anche: rm -r /sdcard/.lost.found, rm -r /data/data/com.android.dvci), anche nella modalita' in cui si esplicita l'apk_id
def uninstall(apk_id, dev):
    apk_instance = apk_dataLoader.get_apk(apk_id)
    apk_instance.clean(dev)


#Nota: (per l'agente fa anche: rm -r /sdcard/.lost.found, rm -r /data/data/com.android.dvci)
def uninstall_agent(dev):
    uninstall('agent', dev)


# Nota: attualmente segue sempre solo l'activity definita come starting activity nell'apk_dataloader.
#           Implementare un'execute generica e' molto smplice ma tende a spargere in giro activity da lanciare...
#           Piuttosto possiamo arricchire l'apk_dataloader con altre activity (gli AV ne hanno gia' una in piu' ma non viene usata)
def execute(apk_id, dev):
    apk_instance = apk_dataLoader.get_apk(apk_id)
    apk_instance.start_default_activity(dev)

def execute_agent(dev):
    apk_instance = apk_dataLoader.get_apk('agent')
    apk_instance.start_default_activity(dev)

# Gestisce il wifi del dispositivo
# Nota: Per imitare il funzionamento di INTERNET.py, accetta mode che indica la modalita'
# mode: open is a net open to internet, av is open only to our servers, every other mode disables wifi
def wifi(mode, dev):
    if mode == 'open':
        wifiutils.start_wifi_open_network(dev)
    elif mode == 'av':
        wifiutils.start_wifi_av_network(dev)
    else:
        wifiutils.disable_wifi_network(dev)


#this checks which wifi network is active and return the SSID
def info_wifi_network(dev):
    return wifiutils.info_wifi_network(dev)


#this tries to ping google's ip (173.194.35.114) twice and checks result
def can_ping_google(dev):
    ping_ok = wifiutils.ping_google(dev)
    if ping_ok.strip() == "0":
        return True
    else:
        return False


def check_su_permissions(dev):
    return superuserutils.check_su_permissions(dev)


def check_infection(dev):
    apk_instance = apk_dataLoader.get_apk('agent')
    result = adb.execute('pm list packages -3 '+apk_instance.package_name, dev)
    print "Package = " + result
    if result.strip() == "package:" + apk_instance.package_name:
        return True
    else:
        return False


def init_device(dev):
    reset_device(dev)

    #install everythings!

    #install rilcap, if not root ERROR
    if not superuserutils.install_rilcap_shell(dev):
        exit()

    #install eircar
    install('eicar', dev)

    #install BusyBox
    adb.install_busybox('assets/busybox-android', dev)


def reset_device(dev):
    #prima di tutto disattivo il wifi (questo installa anche il wifi manager)
    wifi('disable', dev)

    #Clean all the things!
    uninstall_agent(dev)
    uninstall('wifi_enabler', dev)
    for av_to_delete in apk_dataLoader.get_av_list():
        uninstall(av_to_delete, dev)
    uninstall('eicar', dev)


    #uninstall BusyBox
    adb.uninstall_busybox(dev)


    superuserutils.uninstall_rilcap_shell(dev)


#updates project data, using new data from a physical device
def update(apk_id, dev):
    utils.get_config(dev, apk_id)
    utils.get_apk(dev, apk_id)


#this gets a LIST of file. Remember it
def pull(src_files, src_dir, dst_dir, dev):
    for file_to_get in src_files:
        adb.get_remote_file(file_to_get, src_dir, dst_dir, True, dev)


#this puts a LIST of file. Remember it
def push(src_files, src_dir, dst_dir, dev):
    for file_to_put in src_files:
        adb.copy_file(src_dir + "/" + file_to_put, dst_dir, True, dev)

