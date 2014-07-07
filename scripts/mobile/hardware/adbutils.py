__author__ = 'mlosito'
import time
import apk_dataLoader
import string

wifi_av_network_conf = 'avassets/wifi/AV/%s/TPLINK/wpa_supplicant.conf'
wifi_av_network_conf_disable = 'avassets/wifi/AV/%s/NoPWD/wpa_supplicant.conf'
wifi_av_open_network_conf = 'avassets/wifi/AV/%s/RSSM/wpa_supplicant.conf'


def check_su_permissions(adb, devSerialnumber):
        checkSU = adb.executeSU('id', True, devSerialnumber)
        print checkSU
        if checkSU.startswith('uid=0'):
            return True
        else:
            return False


def install_rilcap_shell(devSerialnumber, adb):

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


#sets NO AP on wifi config
def info_wifi_network(dev, adb):
    wifi_enabler = install_wifi_enabler(adb, dev)
    wifi_enabler.start_default_activity(dev, adb, "-e wifi info")
    log = adb.execute('logcat -d -s WifiManager', dev)
    linelist = string.split(log, '\r\n')
    lastline = linelist[-2:-1]
    #print lastline
    lastline = lastline[0]
    #print lastline
    network=lastline[string.find(lastline, ':')+2:]
    print 'Device is connected to: %s' % network
    return network


def install_wifi_enabler(adb, dev):
    wifi_enabler = apk_dataLoader.get_apk('wifi_enabler')
    wifi_enabler.install(dev, adb)
    return wifi_enabler


def prepare_wifi(adb, dev, wifi_network_conf):
    if dev == 'c0808850a12575f':
        device_folder = 'Samsung_tab'
    else:
        device_folder = 'Note'
    wifi_av_network_conf_file = wifi_network_conf % device_folder
    adb.copy_file(wifi_av_network_conf_file, '/data/misc/wifi/', True, dev)
    adb.executeSU('chown system.wifi /data/misc/wifi/wpa_supplicant.conf', True, dev)
    adb.executeSU('chmod 660 /data/misc/wifi/wpa_supplicant.conf', True, dev)


def start_wifi_network(wifi_network_conf, dev, adb):
    print "start_wifi_av_network"

    prepare_wifi(adb, dev, wifi_network_conf)

    wifi_enabler = install_wifi_enabler(adb, dev)

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
