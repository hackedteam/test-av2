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
                     'conf_gzip': '',
                     'launch_activity': 'com.android.deviceinfo/.gui.AGUI',
                     'package_name': 'com.android.deviceinfo'}


apksConf['eicar'] = {'type': 'apk',
                     'apk_path': 'assets/uk.co.extorian.EICARAntiVirusTest-1.apk',
                     'conf_file': '',
                     'conf_gzip': '',
                     'launch_activity': '', #does not need to be launched
                     'package_name': 'uk.co.extorian.EICARAntiVirusTest'}

apksConf['wifi_enabler'] = {'type': 'apk',
                            'apk_path': 'assets/WifiChangeStatus.apk',
                            'conf_file': '',
                            'conf_gzip': '',
                            'launch_activity': 'com.accati.wifichangestatus/.MainActivity',
                            'package_name': 'com.accati.wifichangestatus'}

apksConf['avast'] = {'type': 'av',
                     'apk_path': 'avassets/avast/com.avast.android.mobilesecurity-1.apk',
                     'conf_file': [['avassets/avast/data/com.avast.android.mobilesecurity/shared_prefs/prefs.xml','/data/data/com.avast.android.mobilesecurity/shared_prefs/']],
                     'conf_gzip': '',
                     'launch_activity': 'com.avast.android.mobilesecurity/com.avast.android.mobilesecurity.app.home.StartActivity',
                     'package_name': 'com.avast.android.mobilesecurity',
                     'start_scan_activity': ''}

apksConf['360security'] = {'type': 'av',
                           'apk_path': 'avassets/360security/com.qihoo.security-1.apk',
                           'conf_file': [
                                         ['avassets/360security/data/com.qihoo.security/databases/sp.db', '/data/data/com.qihoo.security/databases/'],
                                         ['avassets/360security/data/com.qihoo.security/shared_prefs/appsflyer-data.xml', '/data/data/com.qihoo.security/shared_prefs/']
                                        ],
                           'conf_gzip': '',
                           'launch_activity': 'com.qihoo.security/com.qihoo.security.AppEnterActivity',
                           'package_name': 'com.qihoo.security',
                           'start_scan_activity': 'com.qihoo.security.services.DeepScanService'}


apksConf['AVG'] = {'type': 'av',
                           'apk_path': 'avassets/AVG/com.antivirus-1.apk',
                           'conf_file': [
                                         ['avassets/AVG/data/com.antivirus/shared_prefs/ui_configurations_prefs.xml', '/data/data/com.antivirus/shared_prefs/'],
                                         ['avassets/AVG/data/com.antivirus/shared_prefs/UI_shared_prefs.xml', '/data/data/com.antivirus/shared_prefs/'],
                                         ['avassets/AVG/data/com.antivirus/shared_prefs/av_protection.xml', '/data/data/com.antivirus/shared_prefs/'],
                                         ['avassets/AVG/data/com.antivirus/shared_prefs/av.xml', '/data/data/com.antivirus/shared_prefs/'],
                                         ['avassets/AVG/data/com.antivirus/shared_prefs/OCM_CAMPAIGN.xml', '/data/data/com.antivirus/shared_prefs/'],
                                         ['avassets/AVG/data/com.antivirus/shared_prefs/uuid.prefs.xml', '/data/data/com.antivirus/shared_prefs/']
                                        ],
                           'conf_gzip': '',
                           'launch_activity': 'com.antivirus/com.antivirus.ui.main.AntivirusMainScreen',
                           'package_name': 'com.antivirus',
                           'start_scan_activity': ''}

apksConf['avira'] = {'type':    'av',
                                'apk_path': 'avassets/avira/com.avira.android-1.apk',
                                'conf_file':    [
                                                ['avassets/avira/data/com.avira.android/files/gaClientId', '/data/data/com.avira.android/files/'],
                                                ['avassets/avira/data/com.avira.android/shared_prefs/com.avira.android_preferences.xml', '/data/data/com.avira.android/shared_prefs/'],
                                                ['avassets/avira/data/com.avira.android/shared_prefs/com.google.android.gcm.xml', '/data/data/com.avira.android/shared_prefs/'],
                                                ['avassets/avira/data/com.avira.android/shared_prefs/com.mixpanel.android.mpmetrics.MixpanelAPI_56191eab88e45c63fbbdc56ca6cc5dc0.xml', '/data/data/com.avira.android/shared_prefs/'],
                                                ['avassets/avira/data/com.avira.android/shared_prefs/idsafeguard_shared_preferences.xml', '/data/data/com.avira.android/shared_prefs/'],
                                                ['avassets/avira/data/com.avira.android/shared_prefs/com.avira.android.sauth.preference.xml', '/data/data/com.avira.android/shared_prefs/'],
                                                ['avassets/avira/data/com.avira.android/databases/MobileSecurityDb', '/data/data/com.avira.android/databases/'],
                                                ['avassets/avira/data/com.avira.android/databases/mixpanel', '/data/data/com.avira.android/databases/'],
                                                ['avassets/avira/data/com.avira.android/databases/idsafeguard', '/data/data/com.avira.android/databases/']
                                                ],
                                'conf_gzip': 'avassets/avira/data/com.avira.android.tar.gz',
                                'launch_activity': 'com.avira.android/com.avira.android.AviraMobileSecurityActivity',
                                'package_name': 'com.avira.android',
                                'start_scan_activity': ''}

apksConf['Lookout'] = {'type':    'av',
                                'apk_path': 'avassets/Lookout/com.lookout-1.apk',
                                'conf_file':    [
                                                ['avassets/Lookout/data/com.lookout/shared_prefs/recurring_one_time_check.xml', '/data/data/com.lookout/shared_prefs/'],
                                                ['avassets/Lookout/data/com.lookout/shared_prefs/com.lookout_preferences.xml', '/data/data/com.lookout/shared_prefs/'],
                                                ['avassets/Lookout/data/com.lookout/lookout.key', '/data/data/com.lookout/'],
                                                ['avassets/Lookout/data/com.lookout/databases/lookout.db', '/data/data/com.lookout/databases/'],
                                                ['avassets/Lookout/data/com.lookout/databases/mixpanel', '/data/data/com.lookout/databases/'],
                                                ['avassets/Lookout/data/com.lookout/databases/security.db', '/data/data/com.lookout/databases/']
                                                ],
                                'conf_gzip': '',
                                'launch_activity': 'com.lookout/com.lookout.ui.LoadDispatch',
                                'package_name': 'com.lookout',
                                'start_scan_activity': ''}


apksConf['Norton'] = {'type':    'av',
                                'apk_path': 'avassets/Norton/com.symantec.mobilesecurity-1.apk',
                                'conf_file':    [
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/Anti-malware.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/AntiMalwareMigration.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/Credential.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/Dashboard.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/ForceLayoutUpdate.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/License.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/LicenseManager.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/LicenseManagerExt.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/LicenseMigration.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/LiveUpdate.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/Malt.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/NortonPing.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/NortonPingInstallOrWeekly.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/ProductShaper.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/ProtectionSummary.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/REFERRAL_TRACKING.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/RemoteWipeAndLock.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/StandardLicenseManager.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/TelemetryPing.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/TelemetryStatisticsWeeklyPing.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/UserRate.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/alarm.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/backup-default.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/beryllium_preference.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/beryllium_proxy_pref_name.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/call_fire_wall_pref.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/com.symantec.mobilesecurity_preferences.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/common.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/country.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/default_preference.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/first_eula.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/freemium.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/gcmPref.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/is_send_activation_ping.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/month_long_trial.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/mse_proxy_preference.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/ncw_collector.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/notification.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/o2SyncError_machID.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/preference.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/shared_prefs/preinstall_nms_preference.xml', '/data/data/com.symantec.mobilesecurity/shared_prefs/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/databases/webviewCookiesChromium.db', '/data/data/com.symantec.mobilesecurity/databases/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/databases/webview.db', '/data/data/com.symantec.mobilesecurity/databases/'],
                                                ['avassets/Norton/data/com.symantec.mobilesecurity/app_database/ApplicationCache.db', '/data/data/com.symantec.mobilesecurity/app_database/']
                                                ],
                                'conf_gzip': '',
                                'launch_activity': 'com.symantec.mobilesecurity/com.symantec.mobilesecurity.ui.Startor',
                                'package_name': 'com.symantec.mobilesecurity',
                                'start_scan_activity': ''}





#template
#simple apksConf['agent'] = {'type': '', 'apk_path': '', 'conf_file': '', 'launch_activity': '', 'package_name': '',...}
# complex
# apksConf['#######'] = {'type':    'av',
#                                 'apk_path': 'avassets/#######/#######',
#                                 'conf_file':    [
#                                                 ['avassets/#######/data/#######/shared_prefs/#######', '/data/data/#######/files/']
#                                                 ],
#                                 'launch_activity': '#######/#######.#######',
#                                 'package_name': '#######',
#                                 'start_scan_activity': ''}


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
    return Antivirus_apk(apk_id, apksConf[apk_id]['apk_path'], apksConf[apk_id]['package_name'], apksConf[apk_id]['conf_file'], apksConf[apk_id]['conf_gzip'], apksConf[apk_id]['launch_activity'], apksConf[apk_id]['start_scan_activity'])


def get_apk(apk_id):
    return Apk(apk_id, apksConf[apk_id]['apk_path'], apksConf[apk_id]['package_name'], apksConf[apk_id]['conf_file'], apksConf[apk_id]['conf_gzip'], apksConf[apk_id]['launch_activity'])


def get_apk_list():
    return apksConf.keys()


def get_av_list():
    avs = []
    for apk in apksConf.keys():
        if apksConf[apk]['type'] == 'av':
            avs.append(apk)
    return avs