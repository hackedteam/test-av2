__author__ = 'fabrizio'

from AVCommon.logger import logging
from AVCommon import command


def on_init(protocol, args):
    pass


def on_answer(vm, success, answer):
    pass


def execute(vm, args):
    from AVAgent import build

    type_ev = args.pop(0)
    key, value = None, None
    if args:
        key, value = args

    target = build.get_target_name()

    logging.debug("target: %s, type_ev: %s, filter: %s=%s" % (target, type_ev, key, value))
    ret = []

    backend = command.context["backend"]
    build.connection.host = backend
    with build.connection() as client:
        logging.debug("connected")

        operation_id, group_id = client.operation('AVMonitor')
        targets = client.targets(operation_id, target)
        if len(targets) != 1:
            return False, "not one target: %s" % len(targets)

        target_id = targets[0]
        instances = client.instances_by_target_id(target_id)
        logging.debug("found these instances: %s" % instances)
        if len(instances) != 1:
            return False, "not one instance: %s" % len(instances)

        instance = instances[0]
        instance_id = instance['_id']
        target_id = instance['path'][1]

        evidences = client.evidences(target_id, instance_id, "type", type_ev)
        for ev in evidences:
            content = ev['data']['content']
            logging.debug("got evidence")
            if key:
                v = ev['data'][key]
                if v == value:
                    return True, "%s: %s -> %s" %(type_ev, key, value)
            else:
                return True, "%s" %(type_ev)
    return False, ret