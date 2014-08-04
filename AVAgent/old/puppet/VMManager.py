import subprocess
import sys
import os


class VMManagerVS:
    def __init__(self, path, host=None, user=None, passwd=None):
        if not host and not user and not passwd:
            self.path = path
        else:
            self.path = path
            self.host = host
            self.user = user
            self.passwd = passwd

    def startup(self, vmx):
        logging.debug("[*] Startup %s!\r\n" % vmx)
        subprocess.call([self.path,
                         "-h", self.host,
                         "-u", self.user, "-p", self.passwd,
                         "start", vmx])

    def shutdown(self, vmx):
        logging.debug("[*] Shutdown %s!\r\n" % vmx)
        subprocess.call([self.path,
                         "-h", self.host,
                         "-u", self.user, "-p", self.passwd,
                         "stop", vmx])

    def reboot(self, vmx):
        logging.debug("[*] Rebooting %s!\r\n" % vmx)
        subprocess.call([self.path,
                         "-h", self.host,
                         "-u", self.user, "-p", self.passwd,
                         "reset", vmx, "soft"])

    def suspend(self, vmx):
        logging.debug("[*] Suspending %s!\r\n" % vmx)
        subprocess.call([self.path,
                         "-h", self.host,
                         "-u", self.user, "-p", self.passwd,
                         "suspend", vmx, "soft"])

    def refreshSnapshot(self, vmx, snapshot):
        logging.debug("[*] Deleting current snapshot.\n")
        subprocess.call([self.path,
                         "-h", self.host,
                         "-u", self.user, "-p", self.passwd,
                         "deleteSnapshot", vmx, snapshot])
        logging.debug("[*] Creating new current snapshot.\n")
        subprocess.call([self.path,
                         "-h", self.host,
                         "-u", self.user, "-p", self.passwd,
                         "snapshot", vmx, snapshot])

    def revertSnapshot(self, vmx, snapshot):
        logging.debug("[*] Reverting to current snapshot.\n")
        subprocess.call([self.path,
                         "-h", self.host,
                         "-u", self.user, "-p", self.passwd,
                         "revertToSnapshot", vmx, snapshot])

    def copyFileToGuest(self, vmx, src_file, dst_file):
        logging.debug("[*] Copying file %s into guest (on dir %s).\n" % (src_file, dst_file))
        subprocess.call([self.path,
                         "-h", self.host,
                         "-u", self.user, "-p", self.passwd,
                         "CopyFileFromHostToGuest", vmx.path, src_file, dst_file])

    def executeCmd(self, vmx, cmd, script=None):
        logging.debug("[*] Executing %s %s.\r\n" % (cmd, script))
        if script is not None:
            subprocess.call([self.path,
                             "-h", self.host,
                             "-u", self.user, "-p", self.passwd,
                             "-gu", vmx.user, "-gp", vmx.passwd,
                             "runProgramInGuest", vmx, cmd, script])
        else:
            subprocess.call([self.path,
                             "-h", self.host,
                             "-u", self.user, "-p", self.passwd,
                             "-gu", vmx.user, "-gp", vmx.passwd,
                             "runProgramInGuest", vmx, cmd])

    def takeScreenshot(self, vmx, out_img):
        logging.debug("[*] Taking screenshot of %s.\n" % vmx)
        subprocess.call([self.path,
                         "-h", self.host,
                         "-u", self.user, "-p", self.passwd,
                         "-gu", vmx.user, "-gp", vmx.passwd,
                         "captureScreen", vmx.path, out_img])


class VMManagerFus:
    def __init__(self, path):
        self.path = path

    def startup(self, vmx):
        logging.debug("[*] Startup %s!\r\n" % vmx)
        subprocess.call([self.path,
                         "-T", "fusion",
                         "start", vmx.path])

    def shutdown(self, vmx):
        logging.debug("[*] Shutdown %s!\r\n" % vmx)
        subprocess.call([self.path,
                         "-T", "fusion",
                         "stop", vmx.path])

    def reboot(self, vmx):
        logging.debug("[*] Rebooting %s!\r\n" % vmx)
        subprocess.call([self.path,
                         "-T", "fusion",
                         "reset", vmx.path, "soft"])

    def suspend(self, vmx):
        logging.debug("[*] Suspending %s!\r\n" % vmx)
        subprocess.call([self.path,
                         "-T", "fusion",
                         "suspend", vmx.path, "soft"])

    def refreshSnapshot(self, vmx):
        logging.debug("[*] Deleting current snapshot.\n")
        subprocess.call([self.path,
                         "-T", "fusion",
                         "deleteSnapshot", vmx.path, vmx.snapshot])
        logging.debug("[*] Creating new current snapshot.\n")
        subprocess.call([self.path,
                         "-T", "fusion",
                         "snapshot", vmx.path, vmx.snapshot])

    def revertSnapshot(self, vmx):
        logging.debug("[*] Reverting to current snapshot.\n")
        subprocess.call([self.path,
                         "-T", "fusion",
                         "revertToSnapshot", vmx.path, vmx.snapshot])

    def copyFileToGuest(self, vmx, src_file, dst_file):
        logging.debug("[*] Copying file %s into guest (on dir %s).\n" % (src_file, dst_file))
        subprocess.call([self.path,
                         "-T", "fusion",
                         "CopyFileFromHostToGuest", vmx.path, src_file, dst_file])

    def executeCmd(self, vmx, cmd, script=None):
        if script is not None:
            logging.debug("[*] Executing %s %s.\r\n" % (cmd, script))
            proc = subprocess.call([self.path,
                                    "-T", "fusion",
                                    "-gu", vmx.user, "-gp", vmx.passwd,
                                    "runProgramInGuest", vmx.path, cmd, script])
        else:
            logging.debug("[*] Executing %s.\r\n" % cmd)
            proc = subprocess.call([self.path,
                                    "-T", "fusion",
                                    "-gu", vmx.user, "-gp", vmx.passwd,
                                    "runProgramInGuest", vmx.path, cmd])
        if proc != 0:
            return False
        return True


    def takeScreenshot(self, vmx, out_img):
        logging.debug("[*] Taking screenshot of %s.\n" % vmx)
        subprocess.call([self.path,
                         "-T", "fusion",
                         "-gu", vmx.user, "-gp", vmx.passwd,
                         "captureScreen", vmx.path, out_img])