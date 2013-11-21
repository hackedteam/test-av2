import logging


""" ends a protocol communication """


def execute(vm, args):
    """ server side """
    logging.debug("    CS Execute")
    return True, "It's time to die"


