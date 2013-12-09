import os
import sys
from AVCommon.logger import logging


from AVCommon import command

def execute(vm, args):
    """ server side """
    logging.debug("    CS Execute")
    assert vm, "null self.vm"
    assert isinstance(args, bool), "INTERNET argument must be boolean"
    #        assert ["on","off"] in args and len(args) == 1, "INTERNET accepts on/off as parameter"
    go = False

    # first time i launched internet
    if "internet_true" not in command.context.keys():
        command.context["internet_true"] = set()
        command.context["internet_false"] = set()

    cmd = None

    if args == True:
        # we want internet on
        if not command.context["internet_true"]:
            cmd = "sudo ../AVMaster/net_enable.sh"

        command.context["internet_true"].add(vm)
        if vm in command.context["internet_false"]:
            command.context["internet_false"].remove(vm)
    else:
        # we want internet off, but we wait the last user

        if not command.context["internet_false"]:
            cmd = "sudo ../AVMaster/net_disable.sh"

        if vm in command.context["internet_true"]:
            command.context["internet_true"].remove(vm)
        command.context["internet_false"].add(vm)


    if cmd:
        ret = os.system(cmd)

        if ret == 0:
            return True, "Internet %s" % args
        else:
            return False, "Failed Internet %s" % args

    return True, "Internet is still %s, but it should change" % args

