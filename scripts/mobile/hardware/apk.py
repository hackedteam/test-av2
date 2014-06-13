class Apk(object):
    def __init__(self, apk_file, uninstall_package_name, apk_conf_files, apk_launch_activity):

        #only apk and uninstall_package_name (apk_to_uninstall) are mandatory
        assert apk_file
        assert uninstall_package_name

        self.apk_file = apk_file
        self.uninstall_package_name = uninstall_package_name
        self.apk_conf_files = apk_conf_files
        self.apk_launch_activity = apk_launch_activity

    def clean(self, dev, adb):
        adb.uninstall(self.uninstall_package_name, dev)

    def install_configuration(self, dev, adb):
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
            adb.execute("am start -n " + self.apk_launch_activity, dev)
        else:
            adb.execute("am start -n " + self.apk_launch_activity + " " + params , dev)