__author__ = 'zeno'

from AVCommon.logger import logging
import time

from AVCommon import command

def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    VM_ALL")

    assert vm, "null vm"
    assert command.context is not None

    vm_all = "360cn,adaware,ahnlab,avast,avast32,avg,avg32,avira,bitdef,comodo,drweb,eset,fsecure,gdata,kis,kis14,kis32,mbytes,mcafee,msessential,norman,norton,panda,risint,trendm,zoneal".split(',')

    assert isinstance(vm_all, list), "VM expects a list"

    command.context["VM"] = vm_all

    logging.debug("items: %s" % (command.context))
    return True, vm_all