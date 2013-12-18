import subprocess
import sys
import os
from AVCommon.logger import logging

from time import sleep
from datetime import datetime
from ConfigParser import ConfigParser

from pysphere import VIServer
from pysphere import VIException

from AVCommon import config


class vSphere:
    def __init__(self, vm_path, sdk_host, sdk_user, sdk_domain, sdk_passwd):
        self.vm_path = vm_path
        self.sdk_host = sdk_host
        self.sdk_user = sdk_domain + "\\" + sdk_user
        self.sdk_passwd = sdk_passwd

    def __enter__(self):
        self.server = VIServer()
        self.server.connect(self.sdk_host, self.sdk_user, self.sdk_passwd)
        if config.verbose:
            logging.debug("connected to vSphere")
        vm = self.server.get_vm_by_path(self.vm_path)
        return vm

    def __exit__(self, type, value, traceback):
        try:
            self.server.disconnect()
            if config.verbose:
                logging.debug("disconnected from vSphere")
        except VIException as e:
            logging.debug("Problem in disconnection. Fault is: %s" % e.fault)
            pass


class VMRun:
    def __init__(self, config_file):
        self.config = ConfigParser()
        self.config.read(config_file)

        self.path = self.config.get("vsphere", "path")
        self.host = self.config.get("vsphere", "host")
        self.domain = self.config.get("vsphere", "domain")
        self.user = self.config.get("vsphere", "user")
        self.passwd = self.config.get("vsphere", "passwd")

    def _run_cmd(self, vmx, cmd, args=[], vmx_creds=[], popen=False, bg=False, timeout=40):
        pargs = [self.path,
                 "-T", "vc",
                 "-h", self.host,
                 "-u", "%s\\%s" % (self.domain, self.user), "-p", self.passwd, cmd, vmx.path]

        if vmx_creds != [] and len(vmx_creds) == 2:
            idx = pargs.index("-p") + 2
            cred = "-gu %s -gp %s" % (vmx_creds[0], vmx_creds[1])
            pargs = pargs[0:idx] + cred.split() + pargs[idx:]

        pargs.extend(args)
        if popen is True:
            return self._run_popen(pargs, timeout)
        elif bg is True:
            if config.verbose:
                logging.debug("running in bg mode")
            return self._run_bg(pargs)
        else:
            return self._run_call(pargs)

    def _run_call(self, pargs):
        if config.verbose:
            logging.debug("_run_call")
        return subprocess.call(pargs)

    def _run_bg(self, pargs):
        if config.verbose:
            logging.debug("_run_bg")
        subprocess.Popen(pargs, stdout=subprocess.PIPE)
        return True

    def _run_popen(self, pargs, timeout=40):
        if config.verbose:
            logging.debug("_run_popen")
        p = subprocess.Popen(pargs, stdout=subprocess.PIPE)

        executed = False
        tick = 0

        while executed is False:
            sleep(20)
            tick += 1
            if p.poll() is not None:  # process is executed and ret.poll() has the return code
                executed = True
            if tick >= timeout * 3:
                logging.debug("run_popen timeout")
                return []
        poll = p.poll()
        if  poll:
            return p.communicate()[0]
        else:
            logging.debug("not poll: %s" % poll)
            return []

    def startup(self, vmx):
        if config.verbose:
            logging.debug("[%s] Starting!\r\n" % vmx)
        self._run_cmd(vmx, "start")

    def shutdown(self, vmx):
        if config.verbose:
            logging.debug("[%s] Stopping!\r\n" % vmx)
        self._run_cmd(vmx, "stop")

    def shutdownUpgrade(self, vmx):
        #["/s","/t","0"])
        r = self.executeCmd(
            vmx, "c:\\WINDOWS\\system32\\shutdown.exe", ["/s", "/t", "0"], timeout=105)
        if r is False:
            return False
        return True

    def reboot(self, vmx):
        if config.verbose:
            logging.debug("[%s] Rebooting!\r\n" % vmx)
        self._run_cmd(vmx, "reset", ["hard"])

    def suspend(self, vmx):
        if config.verbose:
            logging.debug("[%s] Suspending!\r\n" % vmx)
        self._run_cmd(vmx, "suspend", ["soft"])

    def createSnapshot(self, vmx, snapshot):
        if config.verbose:
            logging.debug("[%s] Creating snapshot %s.\n" % (vmx, snapshot))
        self._run_cmd(vmx, "snapshot", [snapshot])

    def deleteSnapshot(self, vmx, snapshot):
        if config.verbose:
            logging.debug("[%s] Deleting snapshot %s.\n" % (vmx, snapshot))
        self._run_cmd(vmx, "deleteSnapshot", [snapshot])

    def revertSnapshot(self, vmx, snapshot):
        if config.verbose:
            logging.debug("[%s] Reverting snapshot %s.\n" % (vmx, snapshot))
        self._run_cmd(vmx, "revertToSnapshot", [snapshot])

    def refreshSnapshot(self, vmx, delete=True):
        untouchables = ["ready", "activated", "_datarecovery_"]

        if config.verbose:
            logging.debug("[%s] Refreshing snapshot.\n" % vmx)

        # create new snapshot
        date = datetime.now().strftime('%Y%m%d-%H%M')
        self.createSnapshot(vmx, "auto_%s" % date)
        if delete is True:
            snaps = self.listSnapshots(vmx)
            logging.debug("%s: snapshots %s" % (vmx,snaps))
            if len(snaps) > 2:
                for s in snaps[1:-1]:
                    logging.debug("checking %s" % s)
                    if s not in untouchables and "manual" not in s:
                        logging.debug("deleting %s" % s)
                        self.deleteSnapshot(vmx, s)
                    else:
                        logging.debug("ignoring %s" % s)

    def revertLastSnapshot(self, vmx):
        snap = self.listSnapshots(vmx)
        if len(snap) > 0:

            for s in range(len(snap) - 1, -1, -1):
                snapshot = snap[s]
                if snapshot != "_datarecovery_":
                    self.revertSnapshot(vmx, snap[s])
                    return "[%s] Reverted with snapshot %s" % (vmx, snap[s])
                else:
                    logging.debug("snapshot _datarecovery_ found!")
            return "%s, ERROR: no more snapshot to try" % vmx
        else:
            return "%s, ERROR: no snapshots!" % vmx

    def mkdirInGuest(self, vmx, dir_path):
        if config.verbose:
            logging.debug("[%s] Creating directory %s.\n" % (vmx, dir_path))
        self._run_cmd(vmx, "CreateDirectoryInGuest", [
            dir_path], [vmx.user, vmx.passwd])

    def listDirectoryInGuest(self, vmx, dir_path):
        if config.verbose:
            logging.debug("[%s] Listing directory %s.\n" % (vmx, dir_path))
        return self._run_cmd(vmx, "listDirectoryInGuest", [dir_path], [vmx.user, vmx.passwd], popen=True)

    def deleteDirectoryInGuest(self, vmx, dir_path):
        if config.verbose:
            logging.debug("[%s] Delete directory %s.\n" % (vmx, dir_path))
        self._run_cmd(
            vmx, "deleteDirectoryInGuest", [dir_path], [vmx.user, vmx.passwd])

    def copyFileToGuest(self, vmx, src_file, dst_file):
        if config.verbose:
            logging.debug("[%s] Copying file from %s to %s.\n" %
                         (vmx, src_file, dst_file))
        return self._run_cmd(vmx, "CopyFileFromHostToGuest",
                             [src_file, dst_file], [vmx.user, vmx.passwd])

    def copyFileFromGuest(self, vmx, src_file, dst_file):
        if config.verbose:
            logging.debug("[%s] Copying file from %s to %s.\n" %
                         (vmx, src_file, dst_file))
        return self._run_cmd(vmx, "CopyFileFromGuestToHost",
                             [src_file, dst_file], [vmx.user, vmx.passwd])

    def executeCmd(self, vmx, cmd, args=[], timeout=40, interactive=True, bg=False):
        if config.verbose:
            logging.debug("[%s] Executing %s with args %s" % (vmx, cmd, str(args)))
        if config.verbose:
            logging.debug("on %s with credentials %s %s" % (vmx, vmx.user, vmx.passwd))
            logging.debug("Options: timeout: %s, interactive: %s, background: %s" % (timeout, interactive, bg))
        cmds = []
        if interactive is True:
            cmds.append("-interactive")
        cmds.append(cmd)
        cmds.extend(args)
        if config.verbose:
            logging.debug("background execution is %s" % bg)
        return self._run_cmd(vmx,
                             "runProgramInGuest",
                             cmds,
                             [vmx.user, vmx.passwd],
                             bg=bg, timeout=timeout)

    def runTest(self, vmx, script):
        return self.executeCmd(vmx, script, interactive=True)

    def listProcesses(self, vmx):
        if config.verbose:
            logging.debug("[%s] List processes\n" % vmx)
        return self._run_cmd(vmx, "listProcessesInGuest", vmx_creds=[vmx.user, vmx.passwd], popen=True)

    def takeScreenshot(self, vmx, out_img):
        if config.verbose:
            logging.debug("[%s] Taking screenshot.\n" % vmx)
        if config.verbose:
            logging.debug("CALLING FUNCTIONS WITH out img %s, u: %s, p: %s.\n" % (out_img, vmx.user, vmx.passwd))
        self._run_cmd(vmx, "captureScreen", [out_img], [vmx.user, vmx.passwd])
        return os.path.exists(out_img)

    def VMisRunning(self, vmx):
        res = self._run_cmd(vmx, "list", popen=True)
        if vmx.path[1:-1] in res:
            return True
        return False

    def listSnapshots(self, vmx):
        out = self._run_cmd(vmx, "listSnapshots", popen=True).split("\n")
        return out[1:-1]
