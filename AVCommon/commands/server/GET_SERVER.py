__author__ = 'zeno'


from AVCommon.logger import logging
from AVCommon import command

def execute(vm, protocol, args):
    """ client side, returns (bool,*) """
    logging.debug("    GET %s" % args)

    assert vm, "null vm"
    assert command.context is not None

    key = args
    if key not in command.context:
        return False, "Key not found: %s" % command.context.keys()
    value = command.context[key]

    logging.debug("key: %s value: %s" % (key, value))
    return True, value