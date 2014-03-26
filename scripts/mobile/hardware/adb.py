#!/usr/bin/python

import subprocess
import re
import shutil
import sys
import threading
import json
import os
import zipfile
from time import sleep

#adb_path = "/Users/olli/Documents/work/android/android-sdk-macosx/platform-tools/adb"
devices = []	# we found with usb devices actually connected
adb_path ="adb";

def call(cmd, device = None):
    if device:
        print "##DEBUG## calling %s for device %s" % (cmd,device)
        proc = subprocess.call([adb_path,
                                "-s", device] + cmd.split(), stdout=subprocess.PIPE)
    else:
        proc = subprocess.call([adb_path] + cmd.split(), stdout=subprocess.PIPE)

    return proc != 0

def execute(cmd, device=None):
    if device:
        proc = subprocess.Popen([adb_path,
                            "-s", device,
                            "shell"] + cmd.split(),
                            stdout=subprocess.PIPE)

    else:
        proc = subprocess.Popen([adb_path,
                            "shell"] + cmd.split(),
                            stdout=subprocess.PIPE)

    comm = proc.communicate()
    return str(comm[0])

def ps(device=None):
    pp = execute("ps", device).strip()
    return pp

def reboot(device = None):
    call("reboot",device)

def get_deviceid(device=None):
    cmd = "dumpsys iphonesubinfo"

    comm =  execute(cmd, device)
    lines = comm.strip()
    devline = lines.split("\n")[2]
    id = devline.split("=")[1].strip()

    return id

def get_properties(device=None):
    def get_prop(property):
        cmd = "getprop %s" % property
        return execute(cmd, device).strip()

    manufacturer = get_prop("ro.product.manufacturer")
    model = get_prop("ro.product.model")
    selinux = get_prop("ro.build.selinux.enforce")
    release_v = get_prop("ro.build.version.release")
#    print manufacturer, model, selinux, release_v
    return { "manufacturer": manufacturer, "model": model, "selinux": selinux, "release":release_v }

#    for line in output.split('\\n'):
#        if 'Device ID' in line:
#            eq = line.find("=")
#            dev_id = line[eq+2:-2]
#            print dev_id
#    return dev_id
	
def install(apk, device=None):
    """ Install melted application on phone
    @param package full path
    @return True/False
    """
    #if os.path.exists(apk) == False:
    #	return False
    if device:
        proc = subprocess.call([adb_path,
                            "-s", device,
                            "install", apk])
                            #,
                            #stdout=subprocess.PIPE)
    else:
        proc = subprocess.call([adb_path,
                                "install", apk])
    if proc != 0:
        return False
    return True

def executeService(apk, device=None):
    """ Execute melted apk on phone
    @param apk class name to run (eg. com.roxy.angrybirds)
    @return True/False
    shell am  startservice -n $CLASS_PACK/
    """
    app = apk + '/.ServiceMain'
    if device:
        proc = subprocess.call([adb_path,
                                "-s", device,
                                "shell", "am", "startservice",
                                "-n", app], stdout=subprocess.PIPE)
    else:
        proc = subprocess.call([adb_path,
                                "shell", "am", "startservice",
                                "-n", app], stdout=subprocess.PIPE)
    if proc != 0:
        return False
    return True

def executeGui(apk, device=None):
    """ Execute melted apk on phone
    @param apk class name to run (eg. com.roxy.angrybirds)
    @return True/False
    shell am  startservice -n $CLASS_PACK/
    """
    app = apk + '/.gui.AGUI'
    if device:
        proc = subprocess.call([adb_path,
                                "-s", device,
                                "shell", "am", "start",
                                "-n", app], stdout=subprocess.PIPE)
    else:
        proc = subprocess.call([adb_path,
                                "shell", "am", "start",
                                "-n", app], stdout=subprocess.PIPE)
    if proc != 0:
        return False
    return True


def uninstall(apk, device=None):
    """ Execute melted apk on phone
    @param apk class name to run (eg. com.roxy.angrybirds)
    @return True/False
    """
    print "##DEBUG## calling uninstall for device %s" % device
    if device:
        proc = subprocess.call([adb_path,
                            "-s", device,
                            "uninstall", apk], stdout=subprocess.PIPE)
    else:
        print "adb uninstall %s" % apk
        proc = subprocess.call([adb_path,
                                "uninstall", apk], stdout=subprocess.PIPE)

    if proc != 0:
        return False

    return True

def get_attached_devices():
    devices = []
    #devices = ""
    # Find All devices connected via USB
    proc = subprocess.Popen([adb_path, "devices"], stdout=subprocess.PIPE)
    output = str(proc.communicate())

    for line in output.split('\\n'):
        if '\\t' in line:
            dev = line.split('\\t')[0]
            props = get_properties(dev)
            #devices += "device: %s model: %s %s\n" % (dev,props["manufacturer"],props["model"])
            devices.append("device: %s model: %s %s" % (dev,props["manufacturer"],props["model"]))

    return devices

"""
	def run(self):
		#apk = 'kr.aboy.tools.zip'
		
		# Change configuration
		#print "Updating package %s with new configuration"  % self.apk
		#if not self.sync_conf():
		#	print "problem updating configuration fo %s." % self.apk
		#	sys.exit(1)
		
		# Unzip apk
		output_zip = os.path.join(conf.build_dir, self.apk)
		output_apk = self.unzip(output_zip)
		
		# Test with adb
		# 1. install
		print "Installing %s on %s" % (output_apk, self.device)
		installed = self.install(output_apk)
		if not installed:
			print "%s not installed on %s" % (output_apk,self.device)
			sys.exit(1)
		
		# 2. run on phone
		print "Executing %s on %s" % (output_apk, self.device)
		executed = self.execute(self.apk[:-4])
		if not executed:
			print "%s not executed on %d" % (output_apk,self.device)
			sys.exit(1)
		
		# 3. check (sleep/wait stuff)
		sleep(10)
		
		# 4. assertions
		print "Checking for instances on %s" % self.device

		# 5. Uninstall phase
		print "This is the end, Uninstalling on %s" % self.device
		uninstalled = self.uninstall(self.apk[:-4])
		if not uninstalled:
			print "Uninstall with your Handz..."
			sys.exit(1)

"""