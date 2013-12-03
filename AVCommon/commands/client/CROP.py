__author__ = 'zeno'

import time
import threading
import logging


thread = None
found = False

def on_init(protocol, args):
    pass


def on_answer(vm, success, answer):
    pass


def execute(vm, args):
    global im1, thread, go_on
    from PIL import ImageGrab

    if args:
        # starts a crop server
        logging.debug("start a crop server")
        im1 = ImageGrab.grab()
        thread = threading.Thread(target=crop, args=(vm,))
        thread.start()
        logging.debug("exiting")
        return True, "%s" % args
    else:
        # stops the crop server
        logging.debug("stop grab_loop")
        go_on = False
        thread.join()
        logging.debug("exiting")
        return not found, "%s" % args


def grab_loop():
    global go_on, found
    i=0;
    found = False
    while go_on:
        i+=1
        found |= crop(i)
        time.sleep(1)
    logging.debug("exiting grab_loop")
    return found

def crop(i):
    global im1

    logging.debug("crop: %s" % i)
    d1= im1.getdata()
    im2 = ImageGrab.grab()
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
        name = "crop_%s.png" % i
        logging.debug("actual crop save: %s" % name)
        print name, c.size
        c.save(name)
