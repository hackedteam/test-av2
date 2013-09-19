import logging

class ignore(object):
    def __init__(self, f):
        logging.debug("inside myDecorator.__init__()")
        self.f = f
        print dir(f)

    def __call__(self):
        logging.debug("inside myDecorator.__call__()")
        #self.f()


class trace(object):
    def __init__(self, f):
        self.f = f

    def __call__(self):
        logging.debug("trace %s, %s" % (self.f.__name__, self.f))
        self.f()


class testingDecorators():
    @ignore
    def myFunction():
        print "hello world"

    @trace
    def execute():
        print "executing"

if __name__ == '__main__':
    t = testingDecorators()
    print "CALL"
    t.myFunction()
    print "END"
    t.execute()
