from AVCommon.logger import logging


""" ends a protocol communication """


def execute(vm, protocol, args):
    """ server side """
    #logging.debug("    CS Execute")

    success = not protocol.error
    return success, "END"


