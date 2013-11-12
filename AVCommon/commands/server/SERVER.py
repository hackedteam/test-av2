import logging

def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    CS Execute: %s" % args)
    assert vm, "null vm"

    ret = eval(args)
    #logging.debug("    CS Execute ret: %s" % ret)
    return True, ret
