import logging

class ignore(object):
    def __init__(self, f):
        logging.debug("inside myDecorator.__init__()")
        self.f = f
        #logging.debug(dir(f))

    def __call__(self):
        logging.debug("inside myDecorator.__call__()")  # pragma: no cover
        #self.f()

__report_indent = [2]


def report(fn):
    """Decorator to print information about a function
    call for use while debugging.
    Prints function name, arguments, and call number
    when the function is called. Prints this information
    again along with the return value when the function
    returns.
    """

    def wrap(*params, **kwargs):
        call = wrap.callcount = wrap.callcount + 1  # pragma: no cover
        indent = ' ' * __report_indent[0]
        fc = "%s" % (fn.__name__)

        logging.debug("%s%s called [#%s]" % (indent, fc, call))
        __report_indent[0] += 1
        ret = fn(*params, **kwargs)
        __report_indent[0] -= 1
        logging.debug("%s%s returned %s [#%s]" % (indent, fc, repr(ret), call))

        return ret
    wrap.callcount = 0
    return wrap


def returns(correct_type):
    def wrap_ext(fn):
        def wrap(*params, **kwargs):
            ret = fn(*params, **kwargs)  # pragma: no cover
            if(not isinstance(ret, correct_type)):
                raise Exception("Wrong type: %s not %s" % (ret, correct_type))
        return wrap
    return wrap_ext

def arguments(correct_type):
    def wrap_ext(fn):  # pragma: no cover
        def wrap(*params, **kwargs):
            ret = fn(*params, **kwargs)
            if(not isinstance(ret, correct_type)):
                raise Exception("Wrong type: %s not %s" % (ret, correct_type))
        return wrap
    return wrap_ext  # pragma: no cover


