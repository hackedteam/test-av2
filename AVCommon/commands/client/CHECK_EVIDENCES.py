__author__ = 'fabrizio'

import logging
from AVCommon import command


def on_init(protocol, args):
    pass


def on_answer(vm, success, answer):
    pass


def execute(vm, args):
    from AVAgent import build

    target = command.context["target"]
    agent = command.context["agent"]

    type_ev, filter = args

    logging.debug("args: %s" % args)
    ret = []
    with build.connection() as client:
        logging.debug("connected")
        target_id, factory_id, ident, operation, target, factory = client.rcs
        ret = client.evidences(target, agent, "type", type_ev)
        if ret:
            logging.debug("got evidences")
            content = ret['data']['content']
            return filter in content, content

    return len(ret)>0, ret