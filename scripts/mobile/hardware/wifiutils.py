__author__ = 'mlosito'
import apk_dataLoader
import string
import adb

import time

RSSM_ssid = "RSSM"
RSSM_psk = "SteveJobsSux!"
TPLINK_ssid = "TP-LINK_9EF638"
TPLINK_psk = "wroadoaqle38lechlesw"

#starts wifi with TPLINK (internal network)
def start_wifi_av_network(dev):
    start_wifi_network(TPLINK_ssid, TPLINK_psk, dev)


#starts wifi with RSSM (OPEN TO INTERNET!!!!)
def start_wifi_open_network(dev):
    start_wifi_network(RSSM_ssid, RSSM_psk, dev)


#sets NO AP on wifi config
def disable_wifi_network(dev):
    wifi_enabler = install_wifi_enabler(dev)
    wifi_enabler.start_default_activity(dev, "-e wifi disable")


#sets NO AP on wifi config
def info_wifi_network(dev):
    wifi_enabler = install_wifi_enabler(dev)
    wifi_enabler.start_default_activity(dev, "-e wifi info")
    log = adb.execute('logcat -d -s WifiManager', dev)
    linelist = string.split(log, '\r\n')
    lastline = linelist[-2:-1]
    #print lastline
    lastline = lastline[0]
    #print lastline
    network=lastline[string.find(lastline, ':')+2:]
    print 'Device is connected to: %s' % network
    return network


def install_wifi_enabler(dev):
    wifi_enabler = apk_dataLoader.get_apk('wifi_enabler')
    wifi_enabler.install(dev)
    return wifi_enabler


def start_wifi_network(ssid, psk, dev):
    print "start_wifi_av_network"
    wifi_enabler = install_wifi_enabler(dev)
    wifi_enabler.start_default_activity(dev, "--es SSID " + ssid + " --es psk " + psk)
    #ensures you are connected to the desired network
    while ssid != info_wifi_network(dev):
        time.sleep(1)
