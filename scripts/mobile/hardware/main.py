# -*- coding: utf-8 -*-

import sys, time
import csv
import os
import inspect
import traceback

import adb

import package
from AVAgent import build

apk = 'assets/installer.default.apk'
service = 'com.android.deviceinfo'

#set timeout via adb: http://osdir.com/ml/android-porting/2011-08/msg00182.html

def test_device(device_id, dev):

    # uninstall device
    adb.uninstall(service, dev)

    # install
    if not adb.install(apk, dev):
        return "installation failed"

    #exeec
    if not adb.executeGui(service, dev):
        return "execution failed"

    # sync e verifica
    time.sleep(60)

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
            instances = c.instances_by_deviceid(device_id, operation_id)
            time.sleep(10)

        instance_id = instances[0]['_id']
        print "instance_id: %s " % instance_id

        info_evidences = []
        counter = 0
        while not info_evidences and counter < 10:
            infos =  c.infos( target_id, instance_id)
            info_evidences = [ e['data']['content'] for e in infos if 'Root' in e['data']['content'] ]
            counter +=1
            time.sleep(10)

        print "info_evidences: %s: " % info_evidences
        if not info_evidences:
            return "No root"

        assert len(info_evidences) > 0
        root_method = info_evidences[0]

        roots = [ r for r in info_evidences if 'previous' not in r ]
        assert len(roots) == 1

        # get "Root: "
        # togliere previous, ne deve rimanere uno

        evidences =  c.evidences( target_id, instance_id )
        device_evidences = [ e['data']['content'] for e in evidences if e['type']=='device' ]
        screenshot_evidences = [ e for e in evidences if e['type']=='screenshot' ]
        print len(device_evidences), len(screenshot_evidences)
        assert len(device_evidences) > 0
        assert len(screenshot_evidences) > 0

        type_evidences = set()
        for e in evidences:
               type_evidences.add(e['type'])
        print type_evidences

        #print info_evidences[0].encode('utf-8')
        #for ev in info_evidences:
        #    print [ e for e in ev.split('\n') if "Root" in e ]

    #uninstall
    adb.uninstall(service, dev)
    adb.reboot(dev)
    time.sleep(120)

    processes = adb.ps(dev)
    running = service in processes

    return "%s, %s" % (root_method, running)

def do_test(dev):
    build.connection.host = "rcs-minotauro"

    with open('tmp/test-%s.csv' % dev, 'ab') as csvfile:
        # write header
        devicelist = csv.writer(csvfile, delimiter=";",
                                quotechar="|", quoting=csv.QUOTE_MINIMAL)
        #devicelist.writerow(["Device", "Android Version", "SELinux Enforce", "root"])

        # getprop device
        device_id = adb.get_deviceid(dev)
        print "device_id: %s" % device_id

        props = adb.get_properties(dev)
        device = "%s %s" % (props["manufacturer"], props["model"])

        try:
            results = test_device(device_id, dev)
        except Exception, ex:
            traceback.print_exc(device_id)
            results = "Error %s" % ex

        devicelist.writerow([ time.time(), device, device_id, props["release"], props["selinux"], results])

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
    dev = raw_input("su quale device si vuole eseguire il test? ")
    print "Eseguo il test su %s" % dev
    do_test(dev)
    print "Fine."

if __name__ == "__main__":
    main()