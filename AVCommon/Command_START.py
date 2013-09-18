import Command


class Command_START(Command.Command):

    """ server side """
    def onInit(self):
        print "DBG onInit"
        pass

    def onAnswer(self, answer):
        print "DBG onAnswer"

    """ client side """
    def Execute(self):
        print "DBG Execute"
        return self.OK


