__author__ = 'mlosito'
from apk import Apk
from antivirus_apk import Antivirus_apk

apk_all = ['agent', 'avast', '360security']
apk_av = ['avast', '360security']

# all data!
apk = {'agent': 'assets/installer.default.apk', 'avast': 'avassets/avast/com.avast.android.mobilesecurity-1.apk', '360security': 'avassets/360security/com.qihoo.security-1.apk'}
#this is a list of av. Every av have an array of couples. Every couples is source and dest of a file.
conf_file = {'agent': '', 'avast': [['avassets/avast/data/com.avast.android.mobilesecurity/shared_prefs/prefs.xml','/data/data/com.avast.android.mobilesecurity/shared_prefs/']], '360security': [['avassets/360security/data/com.qihoo.security/databases/sp.db', '/data/data/com.qihoo.security/databases/'],['avassets/360security/data/com.qihoo.security/shared_prefs/appsflyer-data.xml', '/data/data/com.qihoo.security/shared_prefs/']]}
launch_activity = {'agent': 'com.android.deviceinfo', 'avast': 'com.avast.android.mobilesecurity/com.avast.android.mobilesecurity.app.home.StartActivity', '360security': 'com.qihoo.security/com.qihoo.security.AppEnterActivity'}
apk_to_uninstall = {'agent': 'com.android.deviceinfo', 'avast': 'com.avast.android.mobilesecurity', '360security': 'com.qihoo.security'}

avs_start_scan_activity = {'avast': '', '360security': 'com.qihoo.security.services.DeepScanService'} #to check!


def getGenericApk(apk_id):

    if apk_id not in apk_all:
        return None
    if apk_id in apk_av:
        return getAv(apk_id)
    else:
        return getApk(apk_id)


def getAv(apk_id):
    #collects list of conf files and directories
    return Antivirus_apk(apk[apk_id], apk_to_uninstall[apk_id], conf_file[apk_id], launch_activity[apk_id], avs_start_scan_activity[apk_id])

def getApk(apk_id):
    return Apk(apk[apk_id], apk_to_uninstall[apk_id], conf_file[apk_id], launch_activity[apk_id])
