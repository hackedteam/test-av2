import sys
import csv
import time
import traceback
from com.dtmilano.android.adb.adbclient import AdbClient
import adb


#sys.path.append("/Users/olli/Documents/work/AVTest/")
#sys.path.append("/Users/mlosito/Sviluppo/Rite/scripts/mobile")
sys.path.append("/Users/mlosito/Sviluppo/Rite/")
#sys.path.append("/Users/mlosito/Sviluppo/Rite/AVAgent/")
from AVAgent import build

apk = 'assets/installer.default.apk'
service = 'com.android.deviceinfo'



avs_all = ['avast', '360security']



avs_apk = {'avast': 'avassets/avast/com.avast.android.mobilesecurity-1.apk', '360security': 'avassets/360security/com.qihoo.security-1.apk'}

avs_conf_file = {'avast': 'avassets/avast/data/com.avast.android.mobilesecurity/shared_prefs/prefs.xml', '360security': 'avassets/360security/data/com.qihoo.security/databases/sp.db'}
avs_conf_destination_dir = {'avast': '/data/data/com.avast.android.mobilesecurity/shared_prefs/', '360security': '/data/data/com.qihoo.security/databases/'}
avs_launch_activity = {'avast': 'com.avast.android.mobilesecurity/com.avast.android.mobilesecurity.app.home.StartActivity', '360security': 'com.qihoo.security/com.qihoo.security.AppEnterActivity'}
avs_apk_to_uninstall = {'avast': 'com.avast.android.mobilesecurity', '360security': 'com.qihoo.security'}



