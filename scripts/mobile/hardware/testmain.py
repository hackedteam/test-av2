import sys
import csv
import time
# import datetime
import traceback
from adbclient import AdbClient
import adb

# our files
import adbutils
import utils
#from antivirus_apk import Antivirus_apk
import apk_dataLoader


sys.path.append("/Users/mlosito/Sviluppo/Rite/")
sys.path.append("/Users/zeno/AVTest/")

from AVAgent import build


#avs_to_test = ['avast', '360security', 'AVG']
#avs_to_test = ['AVG']
avs_to_test = ['avira']
avs_all = ['avast', '360security', 'AVG', 'avira', 'Lookout', 'Norton']


#build.connection.host = "rcs-minotauro"
build.connection.host = "rcs-castore"
build.connection.user = "marco"
build.connection.passwd = "passwordP123"

# selinux, no_selinux, rooted (just need to call su)
device_rooting_technique = 'rooted'

def main():
    devices = adb.get_attached_devices()

    print """
    !!! Test AntiVirus !!!
    !!! Attenzione:    !!!
    !!! Prima dell'installazione dell'agente, al dispositivo va impedito il libero accesso ad internet. !!!
    """
    print """ prerequisiti:
    1) Telefono connesso in USB,
    2) USB Debugging enabled (settings/developer options/usb debugging)
    3) connesso wifi TP-LINK_9EF638 <======== NB!!!!!!!!!!!!!!!!!!!!!!!
    4) NESSUNA SIM INSTALLATA <======== NB!!!!!!!!!!!!!!!!!!!!!!!
    5) screen time 2m (settings/display/sleep)
    """

    print "devices connessi:"
    for device in devices:
        print device

    if not devices:
        print "non ci sono device connessi"
    else:

        if len(devices) > 1:
            dev = raw_input("su quale device si vuole eseguire il test? ")
            print "Eseguo il test su %s" % dev

        if len(sys.argv) >= 2:
            serialno = sys.argv[1]

        else:
            serialno = '.*'

        device = AdbClient(serialno=serialno)

        pre_test(device)

        for av in avs_to_test:
            do_test(device, av)

        post_test(device)

    print "Fine."


def test_av(dev, antivirus_apk_instance, results):

    print "##################################################"
    print "##### STAGE 1 : TESTING ANTIVIRUS %s        #####" % antivirus_apk_instance.apk_file
    print "##################################################"

    print "#STEP 1.1: installing AV"
    antivirus_apk_instance.full_install(dev, adb)

    print "#STEP 1.2: starting AV"
    antivirus_apk_instance.start_default_activity(dev, adb)

    print "#STEP 1.3: going online for updates"
    adbutils.start_wifi_open_network(dev,adb)
    raw_input('Now update the av signatures and press Return to continue')

    print "#STEP 1.4: setting the local network to install agent"
    adbutils.start_wifi_av_network(dev,adb)
    raw_input('IF AND ONLY IF YOU ARE CONNECTED TO TPLINK press Return to continue')

    print "#STEP 1.5 WARNING INSTALLING AGENT"
    agent = apk_dataLoader.get_apk('agent')
    agent.install(dev, adb)

    print "#STEP 1.6 WARNING LAUNCHING AGENT"
    agent.start_default_activity(dev,adb)

    print "#STEP 1.7 MANUAL Invisibility check (NB: Check agent launch is no blocked by AV)"
    raw_input('Please check invisibility (and sync) and press Return to continue')

    print "#STEP 1.8 Uninstalling agent"
    agent.clean(dev,adb)

    print "#STEP 1.9 Uninstalling AV"
    antivirus_apk_instance.clean(dev,adb)


def pre_test(device):
    print "###########################################"
    print "##### STAGE 0: PREPARING TEST         #####"
    print "###########################################"
    dev = device.serialno

    #STEP 0.1: uninstall agent
    print "#STEP 0.1: uninstall agent"
    apk_instance = apk_dataLoader.get_apk('agent')
    apk_instance.clean(dev, adb)

    #STEP 0.2: delete wifimanager!
    print "#STEP 0.2: delete wifimanager!"
    apk_instance = apk_dataLoader.get_apk('wifi_enabler')
    apk_instance.clean(dev, adb)


    #STEP 0.3: delete ALL the avs!
    print "#STEP 0.3: delete ALL the avs!"
    for av_to_delete in avs_all:
        av_instance = apk_dataLoader.get_apk_av(av_to_delete)
        av_instance.clean(dev, adb)

    #STEP 0.4: delete EICAR virus
    print "#STEP 0.6: installing EICAR virus"
    eicar_instance = apk_dataLoader.get_apk('eicar')
    eicar_instance.clean(dev, adb)

    #STEP 0.5: install rilcap
    print "#STEP 0.4: install rilcap using: %s", device_rooting_technique
    if not adbutils.install_rilcap_shell(dev, adb, device_rooting_technique):
        exit()

    #STEP 0.6: set wifi to 'protected' network with no access to internet
    print "#STEP 0.5: set wifi to 'protected' network with no access to internet"
    adbutils.start_wifi_av_network(dev, adb)

    #STEP 0.7: installing EICAR virus
    print "#STEP 0.6: installing EICAR virus"
    eicar_instance = apk_dataLoader.get_apk('eicar')
    eicar_instance.install(dev, adb)

    #STEP 0.8: installing BusyBox
    print "#STEP 0.8: installing BusyBox"
    adb.install_busybox('assets/busybox-android', dev)


def post_test(device):

    print "###########################################"
    print "##### STAGE 99: CLOSING TEST          #####"
    print "###########################################"
    dev = device.serialno

    print "#STEP 99.1 deactivating all wifi networks"
    adbutils.clean_wifi_network(dev, adb)

    print "#STEP 99.2 uninstalling AGENT"
    agent_instance = apk_dataLoader.get_apk('agent')
    agent_instance.clean(dev, adb)

    print "#STEP 99.3 uninstalling rilcap"
    print device.shell('rilcap ru')

    print "#STEP 99.4 uninstalling eicar"
    eicar_instance = apk_dataLoader.get_apk('eicar')
    eicar_instance.clean(dev, adb)

    #STEP 99.5: delete wifimanager!
    print "#STEP 99.5: delete wifimanager!"
    apk_instance = apk_dataLoader.get_apk('wifi_enabler')
    apk_instance.clean(dev, adb)

    #STEP 99.6: delete ALL the avs!
    print "#STEP 99.6: delete ALL the avs!"
    for av_to_delete in avs_all:
        av_instance = apk_dataLoader.get_apk_av(av_to_delete)
        av_instance.clean(dev, adb)

    #STEP 99.7: uninstalling BusyBox
    print "#STEP 99.7: uninstalling BusyBox"
    adb.uninstall_busybox(dev)


def do_test(device_id, av):

    # device_id = device #utils.get_deviceId(device)
    # assert device_id
    # assert len(device_id) >= 8

    with open('tmp/test-%s-%s.csv' % (device_id, av), 'wb') as csvfile:
        # write header
        devicelist = csv.writer(csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL)

        #props = get_properties(device, "ro.product.manufacturer", "build.model", "build.selinux.enforce",
                                    # "build.version.release")
        props = utils.get_properties(device_id, av, "ro.product.manufacturer", "ro.product.model",
                                     "ro.build.selinux.enforce", "ro.build.version.release")

        # adds results to csv
        try:
            ret = test_device(device_id, av, props)
            props["return"] = ret
            print "return: %s " % ret
        except Exception, ex:
            traceback.print_exc(utils.get_deviceId(device_id))
            props['error'] = "%s" % ex

        print props
        devicelist.writerow(props.values())


def test_device(device, av, results):
    # extracts serial number (cannot pass an object to command line!)
    dev = device.serialno

    #Starts av installation and stealth check)
    test_av(dev, apk_dataLoader.get_apk_av(av), results)

    # print "Antivirus installed, configured and launched!"

    #return True

    # if not adb.install(apk, dev):
    #     return "installation failed"
    #
    # results["installed"] = True
    # if not adb.executeGui(service, dev):
    #     return "execution failed"
    # else:
    #     results["executed"] = True
    #
    # print "sleep 120"
    # time.sleep(120)
    # print "slept"

    # no skype bacause we have no real network in av testing

    # print "Skype call and sleep"
    # device.shell("am start -a android.intent.action.VIEW -d skype:echo123?call")
    #
    # time.sleep(120)
    #print "slept"

    # print "Checking evidences!"
    #
    # sync_and_check_evidences(operation="QA", target_name="Test 9_3", results=results)

    #check persistance

    # print "reboot"
    # adb.reboot(dev)
    # time.sleep(120)
    #
    # processes = adb.ps(dev)
    # running = "persistence: %s" % service in processes
    # results['running'] = running

    return True


def sync_and_check_evidences(operation, target_name, results):
        # sync e verifica

    with build.connection() as c:

        assert c
        if not c.logged_in():
            return "Not logged in"
        else:
            print "logged in"

        operation_id, group_id = c.operation(operation)
        target_id = c.targets(operation_id, target_name)[0]
        print "target_id: %s" % target_id

        instances = []
        while not instances:
            #print "operation: %s, %s" % (operation_id, group_id)
            print "waiting for sync"
            instances = c.instances_by_deviceid(results["id"], operation_id)
            time.sleep(10)

        instance_id = instances[0]['_id']
        print "instance_id: %s " % instance_id

        info = c.instance_info(instance_id)
        results['instance_name'] = info['name']
        print "instance_info name: %s" % info['name']

        info_evidences = []
        counter = 0
        while not info_evidences and counter < 10:
            infos = c.infos(target_id, instance_id)
            info_evidences = [e['data']['content'] for e in infos if 'Root' in e['data']['content']]
            counter += 1
            time.sleep(10)

        print "info_evidences: %s: " % info_evidences
        if not info_evidences:
            results['root'] = 'No'
            return "No root"

        results['info'] = len(info_evidences) > 0
        root_method = info_evidences[0]
        results['root'] = root_method

        roots = [r for r in info_evidences if 'previous' not in r]
        print "roots: %s " % roots
        assert len(roots) == 1

        # get "Root: "
        # togliere previous, ne deve rimanere uno

        evidences = c.evidences(target_id, instance_id)
        print evidences
        device_evidences = [e['data']['content'] for e in evidences if e['type'] == 'device']
        screenshot_evidences = [e for e in evidences if e['type'] == 'screenshot']
        call_evidences = [e for e in evidences if e['type'] == 'call']
        print len(device_evidences), len(screenshot_evidences), len(call_evidences)

        #assert len(device_evidences) > 0
        #assert len(screenshot_evidences) > 0

        type_evidences = set()
        for e in evidences:
            type_evidences.add(e['type'])
        print type_evidences

        results['evidences'] = type_evidences

        #print info_evidences[0].encode('utf-8')
        #for ev in info_evidences:
        #    print [ e for e in ev.split('\n') if "Root" in e ]

if __name__ == "__main__":
    main()
