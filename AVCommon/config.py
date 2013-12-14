__author__ = 'fabrizio'

from AVCommon import package

class Box:
    def __init__(self):
        pass

    pass


__box = Box()

verbose = False
basedir = False

# dispatcher
skip_to_call = True

#basedir_server = "/opt/AVTest2"
basedir_server = package.basedir
basedir_av = "c:/AVTest"
basedir_logs = "%s/logs" % basedir_av
basedir_crop = "%s/logs/crop" % basedir_av

assert basedir_server
assert basedir_av