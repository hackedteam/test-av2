import os
import sys
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVCommon import command

def execute(vm, args):
    """ server side """
    logging.debug("    CS Execute")
    assert vm, "null self.vm"
    assert isinstance(args, bool), "INTERNET argument must be boolean"
    #        assert ["on","off"] in args and len(args) == 1, "INTERNET accepts on/off as parameter"
    go = False

    # first time i launched internet
    if "internet" not in command.context.keys():
        command.context["internet"] = []

    cmd = None

    if args == True:
        # we want internet on
        command.context["internet"].append(vm)
        cmd = "sudo ../AVMaster/net_enable.sh"
    else:
        # we want internet off, but we wait the last user
        if vm in command.context["internet"]:
            command.context["internet"].remove(vm)
        if not command.context["internet"]:
            cmd = "sudo ../AVMaster/net_disable.sh"

    if cmd:
        ret = os.system(cmd)

        if ret == 0:
            return True, "Internet %s" % args
        else:
            return False, "Failed Internet %s" % args

    return True, "Internet is still %s, but it should change" % args

