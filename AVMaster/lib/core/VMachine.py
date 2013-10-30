import os
import logging

from time import sleep
from ConfigParser import ConfigParser, NoSectionError
from pysphere.resources.vi_exception import VIException
from datetime import datetime

#from VMManager import vSphere
from VMRun import vSphere


class VMachine:

    def __init__(self, name):
        self.name = name
        self.config = None

    def __str__(self):
        return "%s" % self.name

    def get_params(self, conf_file):
        try:
            self.config = ConfigParser()
            self.config.read(conf_file)

            self.path = self.config.get("vms", self.name)

            self.snapshot = self.config.get("vm_config", "snapshot")
            self.user = self.config.get("vm_config", "user")
            self.passwd = self.config.get("vm_config", "passwd")

            self.sdkhost = self.config.get("vsphere","host")
            self.sdkuser = self.config.get("vsphere","user")
            self.sdkdomain = self.config.get("vsphere","domain")
            self.sdkpasswd = self.config.get("vsphere","passwd")

        except NoSectionError:
            logging.debug("VM or VM stuff not found on %s" % conf_file)

    #   FUNCTIONS
    def refresh_snapshot(self, delete=True):
        untouchables = ["ready", "activated", "_datarecovery_"]
        date = datetime.now().strftime('%Y%m%d-%H%M')
        self.create_snapshot(date)
        if delete is True:
            snap_list = self.list_snapshots()
#            for snap in snap_list:
#                print snap.get_name()
            if len(snap_list) > 0 and snap_list[-2].get_name() not in untouchables and "manual" not in snap_list[-2].get_name():
                logging.debug("deleting %s" % snap_list[-2].get_name() )
                self.delete_snapshot(snap_list[-2].get_name())

    def send_files(self, src_dir, dst_dir, filestocopy):
        with vSphere(self.path, self.sdkhost, self.sdkuser, self.sdkdomain, self.sdkpasswd) as vm:

            self._run_vm(vm, "login_in_guest", self.user, self.passwd)

            memo = []
            for filetocopy in filestocopy:
                d, f = filetocopy.split("/")
                src = "%s/%s/%s" % (src_dir, d, f)

                if d == ".":
                    dst = "%s\\%s" % (dst_dir, f)
                else:
                    dst = "%s\\%s\\%s" % (dst_dir, d, f)

                rdir = "%s\\%s" % (dst_dir, d)
                if not rdir in memo:
                    logging.debug("making directory %s " % (rdir))
                    self._run_vm(vm, "make_directory", rdir)
                    memo.append(rdir)

                try:
                    logging.debug("copy %s -> %s" % (src, dst))
                    self._run_vm(vm, "send_file", src, dst)
                except:
                    logging.debug("resending file %s -> %s" % (src, dst))
                    self._run_vm(vm, "send_file", src, dst)

    def get_all_pid(self):
        pids = []
        procs = self.list_processes()

        if procs is None:
            return None

        for proc in procs:
            pids.append(proc['pid'])

        return pids

    def execute_cmd(self, cmd, args=[], timeout=40):
        pid = self.start_process(cmd, args)
        logging.debug("created process %s with pid %s" % (cmd, pid))

        tick = 0

        while pid in self.get_all_pid():
            if tick >= timeout * 6:
                break
            tick += 1
            sleep(10)

        logging.debug(self.get_all_pid())
        logging.debug("exiting")

    def shutdown_upgrade(self, timeout=120):

        tick = 0

        shutdown_cmd = "C:\\WINDOWS\\system32\\shutdown.exe"
        args = ["/s", "/t", "0"]

        self.execute_cmd(shutdown_cmd, args=args)

        while self.is_powered_off() is False:
            if tick >= timeout * 60:
                tick += 1
                sleep(15)
                return False
        return True

    #   TASKS

    def startup(self):
        return self._run_task("power_on")

    def shutdown(self):
        return self._run_task("power_off")

    def suspend(self):
        return self._run_task("suspend")

    def get_snapshots(self):
        return self._run_task("get_snapshots")

    def revert_last_snapshot(self):
        return self._run_task("revert_to_snapshot")

    def create_snapshot(self, name):
        return self._run_task("create_snapshot", name)

    def delete_snapshot(self, name):
        return self._run_task("delete_named_snapshot", name)

    #   COMMANDS

    def is_powered_off(self):
        return self._run_cmd("is_powered_off")

    def is_powered_on(self):
        return self._run_cmd("is_powered_on")

    def login_in_guest(self):
#       print "login with %s and %s" % (self.user, self.passwd)
        return self._run_cmd("login_in_guest", self.user, self.passwd)

    def list_snapshots(self):
        return self._run_cmd("get_snapshots")

    def start_process(self, cmd, args=[]):
        return self._run_cmd("start_process", cmd, args)

    def terminate_process(self, pid):
        return self._run_cmd("terminate_process", pid)

    def list_processes(self):
        self.login_in_guest()
        return self._run_cmd("list_processes")

    # def check_tools(self):
    #   self.login_in_guest()
    #   return self.list_processes()

    #   VM

    def list_directory(self, dir_path):
        with vSphere(self.path) as vm:
            self._run_vm(vm, "login_in_guest", self.user, self.passwd)
            return self._run_vm(vm, "list_files", dir_path)

    def make_directory(self, dst_dir):
        with vSphere(self.path) as vm:
            self._run_vm(vm, "login_in_guest", self.user, self.passwd)
            return self._run_vm(vm, "make_directory", dst_dir)

    def send_file(self, src_file, dst_file):
        with vSphere(self.path) as vm:
            self._run_vm(vm, "login_in_guest", self.user, self.passwd)
            return self._run_vm(vm, "send_file", src_file, dst_file)

    def get_file(self, src_file, dst_file):
        with vSphere(self.path) as vm:
            self._run_vm(vm, "login_in_guest", self.user, self.passwd)
            return self._run_vm(vm, "get_file", src_file, dst_file)

    #   PRIMITIVES

    def _run_vm(self, vm, func, *params):
        try:
            f = getattr(vm, func)

            if len(params) is None:
                return f
            else:
                return f(*params)
        except Exception as e:
            logging.debug("%s, ERROR: Problem running %s. Reason: %s" % (self.name, func, e))

    def _run_cmd(self, func, *params):
        try:
            with vSphere(self.path, self.sdkhost, self.sdkuser, self.sdkdomain, self.sdkpasswd) as vm:
                f = getattr(vm, func)

                if len(params) is None:
                    return f
                else:
                    return f(*params)
        except Exception as e:
            logging.debug("%s, ERROR: Problem running %s. Reason: %s" % (self.name, func, e))

    def _run_task(self, func, *params):

        def wait_for(task):
            s = task.wait_for_state(['success', 'error'])

            if s == 'error':
                logging.debug("ERROR: problem with task %s: %s" % (func, task.get_error_message()))
                return False
            return True

        try:
            with vSphere(self.path, self.sdkhost, self.sdkuser, self.sdkdomain, self.sdkpasswd) as vm:
                f = getattr(vm, func)
                if len(params) is None:
                    task = f(sync_run=False)
                else:
                    task = f(sync_run=False, *params)
                return wait_for(task)
        except Exception as e:
            logging.debug("%s, ERROR: Problem running %s. Reason: %s" % (self.name, func, e))
