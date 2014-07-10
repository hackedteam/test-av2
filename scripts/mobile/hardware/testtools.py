import sys
import csv
import traceback
import time

from adbclient import AdbClient




# our files
import commands
from scripts.mobile.hardware.apk import apk_dataLoader
from scripts.mobile.hardware.utils import wifiutils, superuserutils
import testmain
import utils
import adb


def get_config(device, av):
    dev = device.serialno
    apk = apk_dataLoader.get_apk_av(av)

    adb.install_busybox('assets/busybox-android', dev)
    apk.pack_app_data(dev)
    adb.uninstall_busybox(dev)


def get_apk(device, av):
    dev = device.serialno
    apk = apk_dataLoader.get_apk_av(av)
    apk.retrieve_apk(dev)


def main(argv):
    devices = adb.get_attached_devices()

    print """
    !!! Test AntiVirus !!!
    !!! Attenzione:    !!!
    !!! Prima dell'installazione dell'agente, al dispositivo va impedito il libero accesso ad internet. !!!
    """
    print """ prerequisiti:
    1) Telefono connesso in USB,
    2) USB Debugging enabled (settings/developer options/usb debugging)
    3) NESSUNA SIM INSTALLATA <======== NB!!!!!!!!!!!!!!!!!!!!!!!
    4) screen time 2m (settings/display/sleep)
    """

    print "devices connessi:"
    for device in devices:
        print device

    if not devices:
        print "non ci sono device connessi"
    else:

        if len(devices) > 1:
            dev = raw_input("su quale device si vuole eseguire il test? ")
            print "Eseguo il test su %s" % dev

        if len(sys.argv) >= 2:
            serialno = sys.argv[1]

        else:
            serialno = '.*'

        device = AdbClient(serialno=serialno)
        # print 'Args=', (str(sys.argv))
        # operation = sys.argv[1]

        operation = -1

        while operation != "99":
            print 'What operation do you want to perform?'
            print '1  - get new configuration from installed av'
            print '2  - use net RSSM'
            print '3  - use net TPLINK'
            print '4  - disable net'
            print '5  - clean phone (except rilcap)'
            print '6  - uninstall rilcap'
            print '7  - test all avs'
            print '8  - test a single av'
            print '9  - get wifi network name'
            print '10 - ping google'
            print '11 - is infected?'
            print '12 - got r00t?'
            print '99 - Exit!'

            operation = raw_input()

            if operation == '1':
                print 'Which av you want to retrieve?'
                print str(apk_dataLoader.get_av_list())
                av = raw_input()
                get_config(device, av)
                get_apk(device, av)
            elif operation == '2':
                if not superuserutils.install_rilcap_shell(device.serialno):
                    exit(-1)
                wifiutils.start_wifi_open_network(device.serialno)
            elif operation == '3':
                if not superuserutils.install_rilcap_shell(device.serialno):
                    exit(-1)
                wifiutils.start_wifi_av_network(device.serialno)
            elif operation == '4':
                if not superuserutils.install_rilcap_shell(device.serialno):
                    exit(-1)
                wifiutils.disable_wifi_network(device.serialno)
            elif operation == '5':
                testmain.post_test(device)
            elif operation == '6':
                superuserutils.uninstall_rilcap_shell(device.serialno)
            elif operation == '7':
                pre_test(device)
                for av in apk_dataLoader.get_av_list():
                    do_test(device, av)
                post_test(device)
            elif operation == '8':
                print 'Which av you want to retrieve?'
                print str(apk_dataLoader.get_av_list())
                av = raw_input()
                pre_test(device)
                do_test(device, av)
                post_test(device)
            elif operation == '9':
                if not superuserutils.install_rilcap_shell(device.serialno):
                    exit()
                wifiutils.info_wifi_network(device.serialno)
            elif operation == '10':
                ping_ok = wifiutils.ping_google(device.serialno)
                if ping_ok.strip() == "0":
                    print "I can ping google"
                else:
                    print "I canNOT ping google"
            elif operation == '11':
                if commands.check_infection(device.serialno):
                    print "Infected"
                else:
                    print "Clean"
            elif operation == '12':
                if commands.check_su_permissions(device.serialno):
                    print "Root!"
                else:
                    print "Not root :("

    print "Operazioni terminate"


def test_av(dev, antivirus_apk_instance, results):
    print "##################################################"
    print "#### STAGE 1 : TESTING ANTIVIRUS %s ####" % antivirus_apk_instance.apk_file
    print "##################################################"

    print "#STEP 1.1: installing AV"
    antivirus_apk_instance.full_install(dev)

    print "#STEP 1.2: starting AV"
    antivirus_apk_instance.start_default_activity(dev)

    print "#STEP 1.3: going online for updates"
    wifiutils.start_wifi_open_network(dev)
    raw_input('Now update the av signatures and press Return to continue')

    print "#STEP 1.4: setting the local network to install agent"
    wifiutils.start_wifi_av_network(dev)

    print "#STEP 1.5: checking connection to TPLINK"
    wifiutils.start_wifi_av_network(dev)

    for i in range(1, 100):
        if "TP-LINK_9EF638" == wifiutils.info_wifi_network(dev):
            break
        time.sleep(2)

    print "Net is %s, we go on..." % wifiutils.info_wifi_network(dev)

    print "#STEP 1.6 WARNING INSTALLING AGENT"
    agent = apk_dataLoader.get_apk('agent')
    agent.install(dev)

    print "#STEP 1.7 WARNING LAUNCHING AGENT"
    agent.start_default_activity(dev)

    print "#STEP 1.8 MANUAL Invisibility check (NB: Check agent launch is no blocked by AV)"
    raw_input('Please check invisibility (and sync) and press Return to continue')

    print "#STEP 1.9 Uninstalling agent"
    agent.clean(dev)

    print "#STEP 1.10 Uninstalling AV"
    antivirus_apk_instance.clean(dev)


def pre_test(device):
    print "###########################################"
    print "##### STAGE 0: PREPARING TEST         #####"
    print "###########################################"
    commands.init_device(device.serialno)


def post_test(device):
    commands.reset_device(device.serialno)


def do_test(device_id, av):
    # device_id = device #utils.get_deviceId(device)
    # assert device_id
    # assert len(device_id) >= 8

    with open('tmp/test-%s-%s.csv' % (device_id, av), 'wb') as csvfile:
        # write header
        devicelist = csv.writer(csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL)

        # props = get_properties(device, "ro.product.manufacturer", "build.model", "build.selinux.enforce",
        # "build.version.release")
        props = utils.get_properties(device_id, av, "ro.product.manufacturer", "ro.product.model",
                                     "ro.build.selinux.enforce", "ro.build.version.release")

        # adds results to csv
        try:
            ret = test_device(device_id, av, props)
            props["return"] = ret
            print "return: %s " % ret
        except Exception, ex:
            traceback.print_exc(utils.get_deviceId(device_id))
            props['error'] = "%s" % ex

        print props
        devicelist.writerow(props.values())


def test_device(device, av, results):
    # extracts serial number (cannot pass an object to command line!)
    dev = device.serialno

    # Starts av installation and stealth check)
    test_av(dev, apk_dataLoader.get_apk_av(av), results)


if __name__ == "__main__":
    main(sys.argv)
