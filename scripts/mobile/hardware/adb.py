#!/usr/bin/python

import sys
import subprocess
import json
import re
import shutil
import threading
import os
import zipfile
import time


#adb_path = "/Users/olli/Documents/work/android/android-sdk-macosx/platform-tools/adb"
devices = []  # we found with usb devices actually connected
adb_path = "adb"

temp_remote_path = "/data/local/tmp/in/"

busybox_filename = 'busybox-android'


def call(cmd, device = None):
    if device:
        print "##DEBUG## calling %s for device %s" % (cmd,device)
        proc = subprocess.call([adb_path,
                                "-s", device] + cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        print "##DEBUG## calling %s" % cmd
        proc = subprocess.call([adb_path] + cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return proc != 0


def execute_no_command_split(cmd, device):

    print "##DEBUG## calling %s for device %s" % (cmd,device)

    proc = subprocess.Popen([adb_path,
           "-s", device, "shell", cmd], stdout=subprocess.PIPE)
    comm = proc.communicate()
    # proc.wait()
    return str(comm[0])


def skype_call(device = None):
    #cmd = "am start -a android.intent.action.MAIN -d skype:echo123?call"
    cmd = '"am start -a android.intent.action.VIEW -d skype:echo123?call"'
    return execute(cmd, device)

def execute(cmd, device=None):
    print "##DEBUG## calling %s for device %s" % (cmd, device)
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

    if id == 'null':
        cmd = "settings get secure android_id"
        comm =  execute(cmd, device)
        id = comm.strip()

    return id.replace('*','')

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

#ML
#Copy a single file to an implicit tmp directory
#The destination dir will be /data/local/tmp/in/ (it will be created if nonexistent)
def copy_tmp_file(file_local_path, device=None):

    print "##DEBUG##  Copying a single file to an implicit tmp directory on device %s" % device

    copy_file(file_local_path, temp_remote_path, False, device)


#ML
#Copy a single file to an explicit directory with unprivileged or ROOT privileges
#The destination dir will be created if nonexistent
#it uses a temp directory ("/data/local/tmp/in/") to pull the file and then with root privileges moves the file.
#if the destination is directory "/data/local/tmp/in/", then it doesn't move the file
def copy_file(file_local_path, remote_path, root=False, device=None):

    print "##DEBUG##  Copying a single file to a directory on device %s" % device

    print "create dir %s" % remote_path
    #can always create temp dir without root
    executeSU("mkdir" + " " + temp_remote_path, False, device)

    print "adb push %s" % file_local_path
    if device:
        proc = subprocess.call([adb_path,
                    "-s", device,
                    "push", file_local_path, temp_remote_path], stdout=subprocess.PIPE)
    else:
        proc = subprocess.call([adb_path,
                    "push", file_local_path, temp_remote_path], stdout=subprocess.PIPE)

    if remote_path!=temp_remote_path:
            print "create remote destination %s" % remote_path
            print (executeSU("mkdir" + " " + remote_path, root, device))
            #print (executeSU("id", root, device))

            print "move the file to %s" % remote_path

            print (executeSU("dd" + " if=" + temp_remote_path + "/" + os.path.basename(file_local_path) + " of=" + remote_path + "/" + os.path.basename(file_local_path), root, device))


#Retrieves a single file from device temporary folder using adb pull
#local dir should exists!
#works only with temp dir (because does not use ROOT!)
def get_remote_temp_file(remote_filename, local_destination_path, device=None):
    assert os.path.exists(local_destination_path)

    remote_file_fullpath = temp_remote_path + "/" + remote_filename
    print "adb pull from=%s to=%s" % (remote_file_fullpath, local_destination_path)

    if device:
        proc = subprocess.call([adb_path,
            "-s", device,
            "pull", remote_file_fullpath, local_destination_path], stdout=subprocess.PIPE)
    else:
        proc = subprocess.call([adb_path,
            "pull", remote_file_fullpath, local_destination_path], stdout=subprocess.PIPE)


#Retrieves a single file from device from any folder using dd and adb pull
#local dir should exists!
def get_remote_file(remote_source_filename, remote_source_path, local_destination_path, root=True, device=None):
    assert os.path.exists(local_destination_path)

    remote_file_fullpath_src = remote_source_path + "/" + remote_source_filename
    remote_file_fullpath_tmp = temp_remote_path + "/" + remote_source_filename

    print (executeSU("dd" + " if=" + remote_file_fullpath_src + " of=" + remote_file_fullpath_tmp, root, device))

    print (executeSU("chown " + "shell.shell" + " " + remote_file_fullpath_tmp, root, device))

    get_remote_temp_file(remote_source_filename, local_destination_path, device)

    remove_temp_file(remote_source_filename, device)


#ML
#deletes a single file
def remove_file(filename, file_path, root=False, device=None):

    print "##DEBUG##  Deleting a single file from device %s" % device

    toremove = file_path + "/" + filename

    print "removing file %s" % toremove

    executeSU("rm" + " " + toremove, root, device)


def remove_directory(dir_path, root=False, device=None):

    print "##DEBUG##  Deleting %s directory (rm -r) from device %s" % (dir_path, device)

    executeSU("rm -r" + " " + dir_path, root, device)


#ML
#deletes a single file from tmp
def remove_temp_file(filename, device=None):
    remove_file(filename, temp_remote_path, False, device)


def executeSU(cmd, root=False, device=None):

    if root:
        print "##DEBUG## calling %s for device %s with root %s" % (cmd, device, root)
        print "##DEBUG## executing: %s with rilcap" % cmd
        if device:
            proc = subprocess.Popen(
                [adb_path, "shell", "rilcap qzx '" + cmd + "'"], stdout=subprocess.PIPE)
        else:
            proc = subprocess.Popen([adb_path, "shell", "rilcap qzx '" + cmd + "'"], stdout=subprocess.PIPE)

        comm = proc.communicate()
        return str(comm[0])
    else:
        print "##DEBUG## executing: %s withOUT rilcap" % cmd
        return execute(cmd, device)


#This command installs busybox,
def install_busybox(local_path_with_filename, device=None):
    print 'Installing BusyBox'
    copy_tmp_file(local_path_with_filename)
    #renames file to default (busybox-android)
    #since it's just a rename I can use mv
    executeSU("mv" + " " + temp_remote_path + "/" + os.path.basename(local_path_with_filename) + " " + temp_remote_path + "/" + busybox_filename, False, device)


#NB: this command requires install_busybox!
def uninstall_busybox(device=None):
    print 'Removing BusyBox'
    remove_temp_file(busybox_filename, device)


#NB: this command requires install_busybox!
def execute_busybox(cmd, root=False, device=None):
    print 'Executing with BusyBox cmd= %s' % cmd
    executeSU(temp_remote_path + "/" + busybox_filename + " " + cmd, root, device)


def pack_remote(destination_path_and_filename, source_dir, root=False, device=None):
    print 'Packing'
    execute_busybox("tar -zcvf " + destination_path_and_filename + " " + source_dir, root, device)


def unpack_remote(source_path_and_filename, destination_dir, root=False, device=None):
    print 'Unpacking'
    execute_busybox("tar -zxvf " + source_path_and_filename + " -C " + destination_dir, root, device)


def pack_remote_to_local(remote_source_dir, local_path, local_filename, root=False, device=None):
    remote_file_fullpath = temp_remote_path + "/" + local_filename
    pack_remote(remote_file_fullpath, remote_source_dir, root, device)
    get_remote_temp_file(local_filename, local_path, device)
    remove_temp_file(local_filename, device)


def unpack_local_to_remote(local_file_path, local_filename, remote_dir, root=False, device=None):
    remote_file_fullpath = temp_remote_path + "/" + local_filename
    copy_tmp_file(local_file_path + "/" + local_filename, device)
    unpack_remote(remote_file_fullpath, remote_dir, root, device)
    remove_temp_file(local_filename, device)



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

if __name__ == "__main__":
    print get_deviceid()
