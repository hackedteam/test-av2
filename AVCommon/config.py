__author__ = 'fabrizio'

from AVCommon import package

class Box:
    def __init__(self):
        pass

    pass


__box = Box()

verbose = True
basedir = False

#basedir_server = "/opt/AVTest2"
basedir_server = package.basedir
basedir_av = "c:/AVTest"
basedir_logs = "%s/logs" % basedir_av
basedir_crop = "%s/logs/crop" % basedir_av

redis = "10.0.20.1"

assert basedir_server
assert basedir_av