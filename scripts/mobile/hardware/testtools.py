import sys
import csv
import traceback
import time
import os

from adbclient import AdbClient

# our files
import commands
from scripts.mobile.hardware.apk import apk_dataLoader
from scripts.mobile.hardware.utils import wifiutils, superuserutils, utils
import testmain
import adb


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

        init = raw_input('Init everything? (y/n)')
        if init == "y":
            print "Init!"
            commands.init_device(device.serialno)

        dev = device.serialno

        operation = -1

        while operation != "99":
            print ''
            print '#################       OPERATIONS      #################'
            print 'What operation do you want to perform?'
            print '1  - get new configuration from installed av'
            print '2  - use net RSSM'
            print '3  - use net TPLINK'
            print '4  - disable net'
            print '5  - get wifi network name'
            print '6  - ping google'
            print '7  - test all avs'
            print '8  - test a single av'
            print '9 - is infected?'
            print '10 - got r00t?'
            print '11 - pull file'
            print '12 - push file'
            print ''
            print '#################     INTERNAL TESTS    #################'
            print '20 - test get_server'
            print '21 - test set_server'
            print '22 - test get_client'
            print '23 - test set_client'
            print '24 - test install'
            print '25 - test install_agent'
            print '26 - test uninstall'
            print '27 - test uninstall_agent'
            print '28 - test execute'
            print '29 - test execute_agent'
            print ''
            print '#################          EXIT         #################'
            print '99 - Clean & exit!'

            operation = raw_input()

            if operation == '1':
                print 'Which av you want to retrieve?'
                print str(apk_dataLoader.get_av_list())
                av = raw_input()
                commands.update(av, dev)

            elif operation == '2':
                commands.wifi('open', dev)

            elif operation == '3':
                commands.wifi('av', dev)

            elif operation == '4':
                commands.wifi('disable', dev)

            elif operation == '5':
                print commands.info_wifi_network(dev)

            elif operation == '6':
                if commands.can_ping_google(dev):
                    print "I can ping google"
                else:
                    print "I canNOT ping google"

            elif operation == '7':
                # TODO: andrebbe spostato il do_test
                for av in apk_dataLoader.get_av_list():
                    do_test(device, av)

            elif operation == '8':
                # TODO: andrebbe spostato il do_test
                print 'Which av you want to test?'
                print str(apk_dataLoader.get_av_list())
                av = raw_input()
                do_test(device, av)

            elif operation == '9':
                if commands.check_infection(dev):
                    print "Infected"
                else:
                    print "Clean"

            elif operation == '10':
                if commands.check_su_permissions(dev):
                    print "Root!"
                else:
                    print "Not root :("
            elif operation == '11':
                print '12 - pull file'
                commands.pull(['file.png'], '/sdcard/', 'tmp', dev)
                if os.path.exists('tmp/file.png'):
                    print 'Pull OK!'
                    #debug: time.sleep(20)
                    os.remove('tmp/file.png')
                else:
                    print 'Pull failed!'

            elif operation == '12':
                print '13 - push file'
                commands.push(['file.png'], 'assets', '/sdcard/', dev)

            elif operation == '20':
                print "testvarsrv= " + commands.get_server('testvarsrv')
            elif operation == '21':
                commands.set_server({'testvarsrv': 'testvaluesrv'})
            elif operation == '22':
                print "testvarcli= " + commands.get_client('testvarcli')
            elif operation == '23':
                commands.set_client({'testvarcli': 'testvaluecli'})
            elif operation == '24':
                commands.install('wifi_enabler', dev)
            elif operation == '25':
                commands.install_agent(dev)
            elif operation == '26':
                commands.uninstall('wifi_enabler', dev)
            elif operation == '27':
                commands.uninstall_agent(dev)
            elif operation == '28':
                commands.execute('wifi_enabler', dev)
            elif operation == '29':
                commands.execute_agent(dev)

        print "Operazioni terminate, cleaning time"
        commands.reset_device(dev)
        print "The end"

'''


commands.update()
commands.pull()
commands.push()



wifi
info_wifi_network
can_ping_google
check_su_permissions
check_infection
init_device
reset_device
update
pull
push
'''


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
