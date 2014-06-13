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
    "minotauro": { "backend": "192.168.100.201",
              "frontend": "192.168.100.204",
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


def dev_is_rooted(device):
    packs = device.shell("pm list packages")
    if "com.noshufou.android.su" in packs or "eu.chainfire.supersu" in packs:
        print "the phone is rooted"
        return True
    return False

"""
    build apk on given server with given configuration
"""
def build_apk(kind, srv, factory):
    class Args:
        pass

    report = None

    try:
        srv_params = servers[srv]
    except KeyError:
        return False


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
    args.factory = factory

    build.connection.host = srv_params["backend"]
    #build.connection.user = "avmonitor"
    build.connection.passwd = "Castorep123"

    results, success, errors = build.build(args, report)
    #print "after build", results, success, errors
    return success

"""
    check evidences on server passed as "backend"
"""
def check_evidences(backend, type_ev, key=None, value=None):
#    #backend = command.context["backend"]
#    try:
        build.connection.host = backend
        build.connection.user = "avmonitor"
        build.connection.passwd = "Castorep123"
        success, ret = build.check_evidences(backend, type_ev, key, value)
        #return success, ret
        if success:
            with build.connection() as client:
                instance_id, target_id = build.get_instance(client)
                if not instance_id:
                    print "instance not found"
                    return False, target_id

                evidences = client.evidences(target_id, instance_id, "type", type_ev)
                if evidences:
                    return True, evidences
                return False, "No evidences found for that type"
#    except:
#        return False, "Error checking evidences"
        else:
            return False, "no evidences found at all"

def do_test():
    assert build_apk("silent","castore"), "Build failed. It have to be succeded."
    assert build_apk("silent","castoro") is False, "Build succeded. It have to dont be succeded."

    print "all done"

if __name__ == "__main__":
    do_test()
