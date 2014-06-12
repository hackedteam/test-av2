__author__ = 'mlosito'
from apk import Apk
from antivirus_apk import Antivirus_apk

# apk_all = ['agent', 'avast', '360security']
# apk_av = ['avast', '360security']
# # all data!
# apk = {'agent': 'assets/installer.default.apk', 'avast': 'avassets/avast/com.avast.android.mobilesecurity-1.apk', '360security': 'avassets/360security/com.qihoo.security-1.apk'}
# #this is a list of av. Every av have an array of couples. Every couples is source and dest of a file.
# conf_file = {'agent': '', 'avast': [['avassets/avast/data/com.avast.android.mobilesecurity/shared_prefs/prefs.xml','/data/data/com.avast.android.mobilesecurity/shared_prefs/']], '360security': [['avassets/360security/data/com.qihoo.security/databases/sp.db', '/data/data/com.qihoo.security/databases/'],['avassets/360security/data/com.qihoo.security/shared_prefs/appsflyer-data.xml', '/data/data/com.qihoo.security/shared_prefs/']]}
# launch_activity = {'agent': 'com.android.deviceinfo', 'avast': 'com.avast.android.mobilesecurity/com.avast.android.mobilesecurity.app.home.StartActivity', '360security': 'com.qihoo.security/com.qihoo.security.AppEnterActivity'}
# apk_to_uninstall = {'agent': 'com.android.deviceinfo', 'avast': 'com.avast.android.mobilesecurity', '360security': 'com.qihoo.security'}
# avs_start_scan_activity = {'avast': '', '360security': 'com.qihoo.security.services.DeepScanService'} #to check!

apksConf = {}
apksConf['agent'] = {'type': 'apk',
                     'apk_path': 'assets/installer.default.apk',
                     'conf_file': '',
                     'launch_activity': 'com.android.deviceinfo',
                     'package_name': 'com.android.deviceinfo'}

apksConf['avast'] = {'type': 'av',
                     'apk_path': 'avassets/avast/com.avast.android.mobilesecurity-1.apk',
                     'conf_file': [['avassets/avast/data/com.avast.android.mobilesecurity/shared_prefs/prefs.xml','/data/data/com.avast.android.mobilesecurity/shared_prefs/']],
                     'launch_activity': 'com.avast.android.mobilesecurity/com.avast.android.mobilesecurity.app.home.StartActivity',
                     'package_name': 'com.avast.android.mobilesecurity',
                     'start_scan_activity': ''}

apksConf['360security'] = {'type': 'av',
                           'apk_path': 'avassets/360security/com.qihoo.security-1.apk',
                           'conf_file': [['avassets/360security/data/com.qihoo.security/databases/sp.db', '/data/data/com.qihoo.security/databases/'],
                                         ['avassets/360security/data/com.qihoo.security/shared_prefs/appsflyer-data.xml', '/data/data/com.qihoo.security/shared_prefs/']],
                           'launch_activity': 'com.qihoo.security/com.qihoo.security.AppEnterActivity',
                           'package_name': 'com.qihoo.security',
                           'start_scan_activity': 'com.qihoo.security.services.DeepScanService'}
#template
#apksConf['agent'] = {'type': '', 'apk_path': '', 'conf_file': '', 'launch_activity': '', 'package_name': '',...}

#memoization
apks = {}


# def SET(key, value):
#     apksConf[key] = value

#TODO: boh???
#def build()


def get_generic_apk(apk_id):
    if apk_id in apks.keys():
        return apks[apk_id]

    if not apksConf[apk_id]:
        return None
    if apksConf[apk_id]['type'] == 'av':
        ret = get_apk_av(apk_id)
    else:
        ret = get_apk(apk_id)

    apks[apk_id] = ret
    return ret


def get_apk_av(apk_id):
    #collects list of conf files and directories
    return Antivirus_apk(apksConf[apk_id]['apk_path'], apksConf[apk_id]['package_name'], apksConf[apk_id]['conf_file'], apksConf[apk_id]['launch_activity'], apksConf[apk_id]['start_scan_activity'])


def get_apk(apk_id):
    return Apk(apksConf[apk_id]['apk_path'], apksConf[apk_id]['package_name'], apksConf[apk_id]['conf_file'], apksConf[apk_id]['launch_activity'])
