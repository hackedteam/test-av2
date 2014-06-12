__author__ = 'olli'

import sys
import socket

sys.path.append("/Users/olli/Documents/work/AVTest/")
from AVAgent import build
#from AVCommon import logger
#from AVAgent.build import build


servers = {
    "castore": { "backend": "192.168.100.100",
                 "frontend": "192.168.100.100",
                 "operation": "QA",
                 "target_name": "HardwareFunctional"},
    "polluce": { "backend": "",
                 "frontend": "",
                 "operation": "QA",
                 "target_name": "HardwareFunctional"},
    "zeus": { "backend": "",
              "frontend": "",
              "target_name": "QA",
              "operation": "HardwareFunctional"},
    "minotauro": { "backend": "192.168.100.204",
              "frontend": "192.168.100.201",
              "target_name": "QA",
              "operation": "HardwareFunctional"},
}

params = {
    'platform': 'android',
    'binary': {'demo': False, 'admin': False},
    'sign': {},
    'melt': {}
}


srv_params = {}
dev_params = {}

def set(srv_params, dev_params):
    return srv_params, dev_params

def build_apk(kind, srv):
    class Args:
        pass

    report = None
    print srv, servers[srv]
    srv_params = servers[srv]


    args = Args()

    args.action = "pull"
    args.platform = "android"
    args.kind = kind
    args.backend = srv_params["backend"]
    args.frontend = srv_params["frontend"]
    args.platform_type = "mobile"
    args.operation = srv_params["operation"]
    args.param = params
    args.asset_dir = "assets"

    # servono??
    args.blacklist = ""
    args.soldierlist = ""
    args.nointernetcheck = socket.gethostname()
    args.puppet = "rite"

    build.connection.host = "rcs-castore"
    build.connection.user = "avmonitor"
    build.connection.passwd = "Castorep123"

    results, success, errors = build.build(args, report)
    #print "after build", results, success, errors
    return success

def check_evidences():
    pass


if __name__ == "__main__":
    if build_apk("silent","castore"):
        print "done"

