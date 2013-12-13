__author__ = 'fabrizio'

from AVCommon.logger import logging
from AVCommon import command


def on_init(protocol, args):
    return True


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
        number = 0
        if key:
            for ev in evidences:
                #content = ev['data']['content']
                logging.debug("got evidence")

                v = ev['data'][key]
                if v == value:
                    number+=1
                    logging.debug( "evidence %s: %s -> %s" %(type_ev, key, value))
        else:
            number = len(evidences)

        return number > 0, number
    return False, ret