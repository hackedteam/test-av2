import logging


class ClassName(object):
    """docstring for ClassName"""

    def __init__(self, arg):
        super(ClassName, self).__init__()
        self.arg = arg
        logging.debug("Hello world: %s", arg)

