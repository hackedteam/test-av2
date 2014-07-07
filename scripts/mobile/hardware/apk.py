import os

class Apk(object):
    def __init__(self, apk_file, uninstall_package_name, apk_conf_files, apk_conf_gzip, apk_launch_activity):

        #only apk and uninstall_package_name (apk_to_uninstall) are mandatory
        assert apk_file
        assert uninstall_package_name

        self.apk_file = apk_file
        self.uninstall_package_name = uninstall_package_name
        self.apk_conf_files = apk_conf_files
        self.apk_conf_gzip = apk_conf_gzip
        self.apk_launch_activity = apk_launch_activity

    def clean(self, dev, adb):
        adb.uninstall(self.uninstall_package_name, dev)

    def install_configuration(self, dev, adb):
        if self.apk_conf_gzip != '':
            local_path, local_filename = os.path.split(self.apk_conf_gzip)
            adb.unpack_local_to_remote(local_path, local_filename, '/', True, dev)
        else:
            for conf_file in self.apk_conf_files:
                adb.copy_file(conf_file[0], conf_file[1], True, dev)

    def install(self, dev, adb):
        print self.apk_file
        adb.install(self.apk_file, dev)

    #installs apk and configuration
    def full_install(self, dev, adb):
        self.install(dev, adb)
        self.install_configuration(dev, adb)

    def start_default_activity(self, dev, adb, params=None):
        if not params:
            return adb.execute("am start -n " + self.apk_launch_activity, dev)
        else:
            return adb.execute("am start -n " + self.apk_launch_activity + " " + params, dev)

    def pack_app_data(self, dev, adb):
        local_path, local_filename = os.path.split(self.apk_conf_gzip)
        adb.pack_remote_to_local('/data/data/' + self.uninstall_package_name, local_path, local_filename, True, dev)

    def unpack_app_data(self, dev, adb):
        local_path, local_filename = os.path.split(self.apk_conf_gzip)
        adb.unpack_local_to_remote(local_path, local_filename, '/data/data/' + self.uninstall_package_name, True, dev)

    def retrieve_apk(self, dev, adb):
        apk_path = os.path.dirname(self.apk_file)
        apk_filename = os.path.basename(self.apk_file)
        #print apk_path_clean
        adb.get_remote_file(apk_filename, '/data/app/', apk_path, True, dev)
