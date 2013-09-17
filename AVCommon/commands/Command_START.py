from Command import Command

class Command_START(Command):
    def __init__(self):
        self.super("START")

    """ server side """
    def onInit(self):
        print "DBG onInit"
        pass

    """ client side """
    def onReceive(self):
        print "DBG onReceive"
        return self.OK


