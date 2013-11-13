import logging

from AVCommon import command

def execute(vm, args):
    logging.debug("    CS Execute")
    command.context = {}
    return True, "I'm doing Science and I'm alive"
