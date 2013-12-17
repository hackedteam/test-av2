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


def execute(vm, args):
    from AVMaster import vm_manager

    """ client side, returns (bool,*) """
    logging.debug("    INSTALL_AGENT" )

    protocol, inst_args = args
    mq = protocol.mq

    assert vm, "null vm"
    assert command.context is not None

    cmd = "cd C:\\AVTest\\AVAgent\r\nc:\\python27\\python.exe"
    arg = ["C:\\AVTest\\AVAgent\\av_agent.py", "-m", vm, "-s", mq.session, "-d", config.redis]
    content = "%s %s\r\n" %( cmd, " ".join(arg) )
    fd, filename = tempfile.mkstemp(".bat")

    logging.debug("opening file %s with fd: %s" % (filename, fd))

    os.write(fd, content)
    os.close(fd)

    startup_dir = 'C:/Users/avtest/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup'
    remote_name = "%s/av_agent.bat" % startup_dir
    remote_name= remote_name.replace("/","\\")
    r = vm_manager.execute(vm, "copyFileToGuest", filename, remote_name )

    os.remove(filename)
    if r > 0:
        return False, "Cant Copy %s on VM" % filename

    else:
        return True, "File copied"