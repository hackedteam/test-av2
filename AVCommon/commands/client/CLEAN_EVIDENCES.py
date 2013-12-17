__author__ = 'fabrizio'
from AVCommon.logger import logging
from AVCommon import command


def on_init(protocol, args):
    if not "clean_evidences" in command.context:
        command.context["clean_evidences"] = set()

    ret = None
    if not command.context["clean_evidences"]:
        ret = True

    command.context["clean_evidences"].add(protocol.vm)
    return ret

def on_answer(vm, success, answer):
    pass


def execute(vm, args):
    from AVAgent import build

    backend = command.context["backend"]
    numtargets = build.clean(backend)
    return True, "Cleaned targets: %s" % numtargets
