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
    'platform_type': 'desktop',
    'binary': {'admin': False, 'demo': False},
    'melt': {'admin': False, 'bit64': True, 'codec': True, 'scout': True},
    'platform': 'windows',
    'meltfile': 'AVAgent/assets/windows/meltapp.exe',
    'sign': {},
}


def build_server(kind, platform_type, platform, srv, factory=None):
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
    args.param = params
    args.asset_dir = "/Users/olli/Documents/work/AVTest/AVAgent/assets"

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
    if build_server("silent", "desktop", "windows", "castore") is False:
        print "problem build from server"

if __name__ == "__main__":
    main()