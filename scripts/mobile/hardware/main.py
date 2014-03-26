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

def test_device(device_id):

    # uninstall device
    adb.uninstall(service)

    # install
    if not adb.install(apk):
        return "installation failed"

    print "installed"
    #exeec
    if not adb.executeGui(service):
        return "execution failed"
    else:
        print "executed"

    # sync e verifica
    time.sleep(60)
    print "slept"

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

        info = c.instance_info(instance_id)
        instance_name =  info['name']
        print "instance_info name: %s" % instance_name

        info_evidences = []
        counter = 0
        while not info_evidences and counter < 10:
            infos =  c.infos( target_id, instance_id)
            info_evidences = [ e['data']['content'] for e in infos if 'Root' in e['data']['content'] ]
            counter +=1
            time.sleep(10)

        print "info_evidences: %s: " % info_evidences
        if not info_evidences:
            return "%s , No root" % instance_name

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
    adb.uninstall(service)
    adb.reboot()
    time.sleep(120)

    processes = adb.ps()
    running = service in processes

    return "%s, %s, %s" % (instance_name, root_method, running)

def main():
    build.connection.host = "rcs-minotauro"

    print """ prerequisiti:
    1) Telefono connesso in USB,
    2) USB Debugging enabled (settings/developer options/usb debugging)
    3) connesso wifi a RSSM
    4) screen time 2m (settings/display/sleep)
    """

    with open('test.csv', 'ab') as csvfile:
        # write header
        devicelist = csv.writer(csvfile, delimiter=";",
                                quotechar="|", quoting=csv.QUOTE_MINIMAL)
        #devicelist.writerow(["Device", "Android Version", "SELinux Enforce", "root"])

        # getprop device
        device_id = adb.get_deviceid()
        print "device_id: %s" % device_id

        props = adb.get_properties()
        device = "%s %s" % (props["manufacturer"], props["model"])

        try:
            results = test_device(device_id)
        except Exception, ex:
            traceback.print_exc(device_id)
            results = "Error %s" % ex

        line = [ time.time(), device, device_id, props["release"], props["selinux"], results]
        print line
        devicelist.writerow(line)


if __name__ == "__main__":
    main()