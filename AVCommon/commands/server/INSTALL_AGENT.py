__author__ = 'fabrizio'

import os
import sys
import glob
from AVCommon.logger import logging
from AVCommon import config
import time
import tempfile

from AVCommon import command

vm = None


def execute(vm, protocol, inst_args):
    from AVMaster import vm_manager

    """ client side, returns (bool,*) """
    logging.debug("    INSTALL_AGENT" )
    mq = protocol.mq

    assert vm, "null vm"
    assert command.context is not None

    cmd = "rmdir /s /q C:\\AVTest\\AVAgent\\running \r\n"\
          "cd C:\\AVTest\\AVAgent\r\n" \
          "c:\\python27\\python.exe"
    arg = ["C:\\AVTest\\AVAgent\\av_agent.py", "-m", vm, "-s", mq.session, "-d", config.redis]
    start_bat = "%s %s\r\n" %( cmd, " ".join(arg) )

    agent_bat = "start /min C:\\AVTest\\AVAgent\\start.bat ^& exit\r\n"

    fd, filename = tempfile.mkstemp(".bat")
    logging.debug("opening file %s with fd: %s" % (filename, fd))
    os.write(fd, agent_bat)
    os.close(fd)

    startup_dir = 'C:/Users/avtest/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup'
    remote_name = "%s/av_agent.bat" % startup_dir
    remote_name= remote_name.replace("/","\\")
    r = vm_manager.execute(vm, "copyFileToGuest", filename, remote_name )
    os.remove(filename)

    fd, filename = tempfile.mkstemp(".bat")
    logging.debug("opening file %s with fd: %s" % (filename, fd))
    os.write(fd, start_bat)
    os.close(fd)

    remote_name = "C:\\AVTest\\AVAgent\\start.bat"
    r = vm_manager.execute(vm, "copyFileToGuest", filename, remote_name )
    os.remove(filename)

    dirname = "%s/avagent/running" % config.basedir_av
    r = vm_manager.execute(vm, "deleteDirectoryInGuest", dirname)


    if r > 0:
        return False, "Cant Copy %s on VM" % filename

    else:
        return True, "File copied"
