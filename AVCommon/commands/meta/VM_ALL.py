__author__ = 'zeno'

from AVCommon.logger import logging
import time

from AVCommon import command

def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    VM_ALL")

    assert vm, "null vm"
    assert command.context is not None

    protocol, level = args

    vm_first = "avast,avast32,avg,avg32,avira,kis,kis14,kis32,mcafee,norton,panda,comodo,eset,msessential".split(',')
    vm_second = "360cn,adaware,ahnlab,bitdef,drweb,fsecure,gdata,mbytes,norman,risint,trendm,zoneal".split(',')

    if level and level.lower() == "important":
        vm_all = vm_first
    elif level and level.lower() == "irrilevant":
        vm_all = vm_second
    else:
        vm_all = vm_first + vm_second
    assert isinstance(vm_all, list), "VM expects a list"

    command.context["VM"] = vm_all

    logging.debug("items: %s" % (command.context))
    return True, vm_all