__author__ = 'fabrizio'

from AVCommon.logger import logging
from AVCommon import command


def on_init(protocol, args):
    pass


def on_answer(vm, success, answer):
    pass


def execute(vm, args):
    from AVAgent import build

    #target = command.context["target"]
    #agent = command.context["agent"]

    type_ev, prog = args[0:2]
    target = None
    #target = 'VM_%s' % self.hostname

    if len(args)>2:
        target = args[2]

    logging.debug("type_ev:%s, filter: %s" % (type_ev, prog))
    ret = []

    backend = command.context["backend"]
    build.connection.host=backend
    with build.connection() as client:
        logging.debug("connected")

        if not target:
            logging.debug("rcs: %s" % (str(build.connection.rcs)))
            target_id, factory_id, ident, operation, target, factory = build.connection.rcs


        instances = client.instances_by_name(target)
        logging.debug("found these instances: %s" % instances)
        if len(instances) != 1:
            return False, "not one instance: %s" % len(instances)

        instance = instances[0]
        instance_id = instance['_id']
        target_id = instance['path'][1]

        evidences = client.evidences(target_id, instance_id, "type", type_ev)
        for ev in evidences:
            content = ev['data']['content']
            program = ev['data']['program']
            logging.debug("got evidence: %s: %s" %(program, content))
            if prog == program:
                return True, "%s: %s" %(program, content)

    return False, ret