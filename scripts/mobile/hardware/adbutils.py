__author__ = 'mlosito'
import time
import apk_dataLoader

wifi_av_network_conf = 'avassets/wifi/AV/Note/TPLINK/wpa_supplicant.conf'
wifi_av_network_conf_disable = 'avassets/wifi/AV/Note/NoPWD/wpa_supplicant.conf'
wifi_av_open_network_conf = 'avassets/wifi/AV/Note/RSSM/wpa_supplicant.conf'

def install_rilcap_shell(devSerialnumber, adb, selinux=False):
        if selinux:
            #installs SUIDEXT shell
            #installs (to tmp) necessary files for root (rilcap shell installing)
            adb.copy_tmp_file("avassets/android_exploit/selinux_exploit", devSerialnumber)
            adb.copy_tmp_file("avassets/android_exploit/selinux_suidext", devSerialnumber)
            #installs RILCAP
            adb.call('shell /data/local/tmp/in/selinux_exploit "selinux_suidext rt"', devSerialnumber)

        else:
            #installs (to tmp) necessary files for root (rilcap shell installing)
            adb.copy_tmp_file("avassets/android_exploit/local_exploit", devSerialnumber)
            adb.copy_tmp_file("avassets/android_exploit/suidext", devSerialnumber)
            #installs RILCAP /data/local/tmp/in/local_exploit "/data/local/tmp/in/suidext rt"
            adb.call('shell /data/local/tmp/in/local_exploit "/data/local/tmp/in/suidext rt"', devSerialnumber)

        #todo remove temp files


def uninstall_rilcap_shell(devSerialnumber, adb):
        #uninstalls RILCAP - adb shell rilcap ru
        adb.call('shell rilcap ru', devSerialnumber)

#starts wifi with TPLINK (internal network)
def start_wifi_av_network(dev, adb):
    start_wifi_network(wifi_av_network_conf, dev, adb)

#starts wifi with RSSM (OPEN TO INTERNET!!!!)
def start_wifi_open_network(dev, adb):
    start_wifi_network(wifi_av_open_network_conf, dev, adb)

#sets NO AP on wifi config
def clean_wifi_network(dev, adb):
    start_wifi_network(wifi_av_network_conf_disable, dev, adb)


def start_wifi_network(wifi_network_conf, dev, adb):
    print "start_wifi_av_network"
    adb.copy_file(wifi_network_conf, '/data/misc/wifi/', True, dev)
    adb.executeSU('chown system:wifi /data/misc/wifi/wpa_supplicant.conf', True, dev)
    adb.executeSU('chmod 660 /data/misc/wifi/wpa_supplicant.conf', True, dev)

    wifi_enabler = apk_dataLoader.get_apk('wifi_enabler')

    wifi_enabler.install(dev, adb)
    wifi_enabler.start_default_activity(dev, adb, "-e wifi false")
    time.sleep(1)
    wifi_enabler.start_default_activity(dev, adb, "-e wifi true")

    # adb.executeSU('ifconfig wlan0 down', True, dev)
    #works only under cyanogen
    #adb.executeSU('echo terminate | wpa_cli', True, dev)
    # print "reboot"
    # adb.reboot(dev)
    # raw_input("Please press a key when reboot is complete")

    # time.sleep(120)

    # #cat /etc/wifi/wpa_supplicant.conf /data/local/tmp/in/wpa_supplicant.conf > /data/misc/wifi/wpa_supplicant.conf