__author__ = 'fabrizio'

import os
from AVCommon.logger import logging
from AVCommon import command

def on_init(protocol, args):
    pass


def on_answer(vm, success, answer):
    pass


def execute(vm, args):
    from AVAgent import build
    logging.debug("    CS CHECK_EMPTY_DIR:  %s,%s" % (vm, str(args)))

    assert isinstance(args, list)
    dirs, whitelist = args
    assert isinstance(dirs, list)
    assert isinstance(whitelist, list)

    wl = set(whitelist)

    success = True
    res = []
    for dir in dirs:
        if not os.path.exists(dir):
            success |= True
            #res.append("Not existent dir: %s" % dir)
            logging.info("Not existent dir: %s" % dir)
        else:
            l = set(os.listdir(dir))
            files_remained=l.difference(wl)

            if l and wl and not files_remained:
                logging.debug("all the files are whitelist: %s" % l)

            if not files_remained:
                success |= True
                #res.append("Empty dir: %s" % dir)
                logging.info("Empty dir: %s" % dir)
            else:
                success |= False
                res.append("Non empty dir %s: %s" % (dir,files_remained))
                logging.info("Non empty dir %s: %s" % (dir,files_remained))

    logging.debug("CHECK_EMPTY: %s, %s" % (success, res))
    return success, res