__author__ = 'mlosito'


wifi_av_network_conf = 'avassets/wpa_supplicant.conf'


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
    adb.copy_file(wifi_av_network_conf, '/data/misc/wifi', True, dev)
    adb.executeSU('svc wifi disable', True, dev)
    adb.executeSU('svc wifi enable', True, dev)