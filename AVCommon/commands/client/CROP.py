__author__ = 'zeno'

import time
import threading
from AVCommon.logger import logging
import os

thread = None
found = []
go_on = True

def on_init(protocol, args):
    return True

from AVCommon import config

def on_answer(vm, success, answer):
    from AVMaster import vm_manager
    logging.debug("CROP answer: %s|%s" % (success, answer))
    # answer = ['crop/1.png','crop/3.png']
    if not success:
        if not answer or not isinstance(answer, list) :
            return

        logging.warn("We have to PULL images: %s" % answer)
        dir = "%s/logs/crop" % config.basedir_server

        for src in answer:
            try:
                name = src.split('/')[1]
                dst_dir = "%s/%s" %(dir, vm)
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                dst = "%s/%s" % (dst_dir, name)

                src_av = "%s/%s" % (config.basedir_av, src)
                logging.debug("PULL: %s -> %s" % (src, dst))
                vm_manager.execute(vm, "copyFileFromGuest",src_av ,dst)
            except:
                logging.exception("Cannot get image %s" % src)

def execute(vm, args):
    from PIL import ImageGrab
    global im1, thread, go_on, found

    if args:
        # starts a crop server
        logging.debug("start a crop server")

        im1 = ImageGrab.grab()
        thread = threading.Thread(target=grab_loop, args=(vm,))
        thread.start()
        logging.debug("exiting")
        return True, "%s" % args
    else:
        # stops the crop server
        logging.debug("stop grab_loop")
        go_on = False
        if thread:
            thread.join()
        logging.debug("exiting, returning %s" % found)
        success = len(found) == 0
        return success, found

def grab_loop(vm):
    global go_on, found
    iter=0;
    logging.debug("grab loop")
    if not os.path.exists("crop"):
        os.mkdir("crop")

    while go_on:
        iter+=1
        f = crop(iter)
        if f=="ERROR":
            return

        if f:
            found.append(f)
        time.sleep(2)
    logging.debug("exiting grab_loop, found: " % found)
    #return found


def crop(iter):
    from PIL import ImageGrab
    global im1

    logging.debug("crop: %s" % iter)
    d1= im1.getdata()
    try:
        im2 = ImageGrab.grab()
    except:
        logging.exception("Cannot grab")
        return "ERROR"

    d2=im2.getdata()

    w = d1.size[0]
    h = d1.size[1] - 20
    l,r,t,b = w,0,h,0

    for y in range(h):
        for x in range(w):
            i = y * w + x
            assert i < w*h
            if(d1[i] != d2[i]):
                #print x,y
                l = min(x,l)
                r = max(x,r)
                b = max(y,b)
                t = min(y,t)

    logging.debug("crop box: %s" % str((l,t,r,b)))

    c=im2.crop((l,t,r,b))
    im1 = im2
    if c.size[0] > 20 and c.size[1] > 20:
        name = "crop/%s.png" % iter
        logging.debug("actual crop save: %s" % name)
        logging.debug("name: %s size: %s" % ( name, c.size ))
        c.save(name)
        return name

    return None
