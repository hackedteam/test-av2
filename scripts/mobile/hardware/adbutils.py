__author__ = 'mlosito'
import time

wifi_av_network_conf = 'avassets/wifi/AV/Note/wpa_supplicant.conf'
wifi_av_network_conf_disable = 'avassets/wifi/AV/NoPWD/wpa_supplicant.conf'

def install_rilcap_shell(devSerialnumber, adb):
        #installs (to tmp) necessary files for root (rilcap shell installing)
        adb.copy_tmp_file("avassets/android_exploit/local_exploit", devSerialnumber)
        adb.copy_tmp_file("avassets/android_exploit/suidext", devSerialnumber)
        #installs RILCAP
        adb.call('shell /data/local/tmp/in/local_exploit "suidext rt"', devSerialnumber)
        #todo remove temp files


def uninstall_rilcap_shell(devSerialnumber, adb):
        #uninstalls RILCAP - adb shell rilcap ru
        adb.call('shell rilcap ru', devSerialnumber)


def start_wifi_av_network(dev, adb):
    adb.copy_file(wifi_av_network_conf, '/data/misc/wifi/', True, dev)
    adb.executeSU('chown system /data/misc/wifi/wpa_supplicant.conf', True, dev)
    adb.executeSU('chgrp wifi /data/misc/wifi/wpa_supplicant.conf', True, dev)
    adb.executeSU('chmod 660 /data/misc/wifi/wpa_supplicant.conf', True, dev)

    #works only under cyanogen
    #adb.executeSU('echo terminate | wpa_cli', True, dev)
    print "reboot"
    adb.reboot(dev)
    time.sleep(120)
    #cat /etc/wifi/wpa_supplicant.conf /data/local/tmp/in/wpa_supplicant.conf > /data/misc/wifi/wpa_supplicant.conf


def clean_wifi_network(dev, adb):
    adb.copy_file(wifi_av_network_conf_disable, '/data/misc/wifi/', True, dev)
    #adb.executeSU('rm /data/misc/wifi/wpa_supplicant.conf', True, dev)
    print "reboot"
    adb.reboot(dev)
    time.sleep(120)
    #adb.executeSU('cat /etc/wifi/wpa_supplicant.conf > /data/misc/wifi/wpa_supplicant.conf', True, dev)
