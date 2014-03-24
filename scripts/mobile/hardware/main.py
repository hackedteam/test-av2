import sys
import csv

import adb,api

apk = 'installer.default.apk'

def main():

    with open('test.csv', 'wb') as csvfile:
        # write header
        devicelist = csv.writer(csvfile, delimiter=";",
                                quotechar="|", quoting=csv.QUOTE_MINIMAL)
        devicelist.writerow(["Device", "Android Version", "SELinux Enforce", "root"])

        # getprop device
        props = adb.get_properties()
        device = "%s %s" % (props["manufacturer"],props["model"])
        devicelist.writerow([device, props["release"], props["selinux"], ""])

        # install
        '''
        if not adb.install(apk):
            print "installation failed"
            sys.exit(1)

        #exeec
        if not adb.execute():
            print "execution failed"
            sys.exit(1)
        '''

        # sync e verifica


        # get loginfo | grep root


        # get evidences screenshot


        # output su file excel csv


        #uninstall
        #print adb.uninstall("com.viber.voip")


if __name__ == "__main__":
    main()